"""
Karmaworld Dictionary helpers
Finals Club (c) 2014
Author: Bryan Bonvallet
"""

# I'd wager none of these are thread safe.

import re
from collections import MutableMapping


needs_mapping = re.compile('{[a-zA-Z_]\w*}')


class attrdict(object):
    """ Access dictionary by object attributes. """
    def __getattr__(self, attr):
        # create call stack, if not already there, to avoid loops
        try:
            callstack = object.__getattribute__(self, '__callstack')
        except AttributeError:
            object.__setattr__(self, '__callstack', [])
            callstack = object.__getattribute__(self, '__callstack')

        try:
            # don't call something already on the stack
            if attr in callstack:
                raise KeyError()
            # track this attribute before possibly recursing
            callstack.append(attr)
            retattr = self.__getitem__(attr)
            # success, remove attr from stack
            callstack.remove(attr)
            return retattr
        except KeyError:
            # if code is here, attr is not in dict
            try:
                # try to grab attr from the object
                retattr = super(attrdict, self).__getattribute__(attr)
                return retattr
            finally:
                # remove stack now that the attribute succeeded or failed
                callstack.remove(attr)

    def __setattr__(self, attr, value):
        self.__setitem__(attr, value)

    def __delattr__(self, attr):
        self.__delitem__(attr)


class fallbackdict(MutableMapping, attrdict):
    """
    Retrieve default values from a fallback dictionary and dynamically .format
    """
    def __init__(self, fallback, *args, **kwargs):
        """
        Supply dictionary to fall back to when keys are missing.
        Other arguments are handled as normal dictionary.
        """
        # dodge attrdict problems by using object.__setattr__
        classname = type(self).__name__
        object.__setattr__(self, '_{0}__internaldict'.format(classname), {})
        object.__setattr__(self, '_{0}__fallback'.format(classname), fallback)
        object.__setattr__(self, '_{0}__fetching'.format(classname), [])
        super(fallbackdict, self).__init__(*args, **kwargs)

    def __needs_format__(self, value):
        """ Helper to determine when a string needs formatting. """
        return hasattr(value, 'format') and needs_mapping.search(value)

    def __getitem__(self, key):
        """
        Use this dict's value if it has one otherwise grab value from parent
        and populate any strings with format keyword arguments.
        """
        indict = self.__internaldict
        fetching = self.__fetching

        local = (key in indict)
        # this will throw a key error if the key isn't in either place
        # which is desirable
        value = indict[key] if local else self.__fallback[key]

        if (key in fetching) or (not self.__needs_format__(value)):
            # already seeking this key in a recursed call
            # or it doesn't need any formatting
            # so return as-is
            return value

        # if the code is this far, strings needs formatting
        # **self will call this function recursively.
        # prevent infinite recursion from e.g. d['recurse'] = '{recurse}'
        fetching.append(key)
        value = value.format(**self)
        # undo infinite recursion prevention
        fetching.remove(key)
        return value

    def __setitem__(self, key, value):
        """
        Set the internal dict with key/value.
        """
        self.__internaldict[key] = value

    def __delitem__(self, key):
        """ Delete the key from the internal dict. """
        del self.__internaldict[key]

    def __uniquekeys__(self):
        """ Returns unique keys between this dictionary and the fallback. """
        mykeys = set(self.__internaldict.keys())
        fbkeys = set(self.__fallback.keys())
        # set union: all keys from both, no repeats.
        return (mykeys | fbkeys)

    def __iter__(self):
        """ Returns the keys in this dictionary and the fallback. """
        return iter(self.__uniquekeys__())

    def __len__(self):
        """
        Returns the number of keys in this dictionary and the fallback.
        """
        return len(self.__uniquekeys__())
