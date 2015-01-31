import re
import bleach
import html5lib
from html5lib.constants import tokenTypes
from bleach.sanitizer import BleachSanitizer
from bleach import _render
import bleach_whitelist
from bs4 import BeautifulSoup

def _canonical_link_predicate(tag):
    return tag.name == u'link' and \
        tag.has_attr('rel') and \
        u'canonical' in tag['rel']

class Sanitizer(BleachSanitizer):
    """
    The default bleach clean method uses a sanitizer that handles disallowed
    tags either by escaping them. With the bad HTML 

        <script>alert('bad')</script>

    if ``strip=False``, bleach will output:
    
        &lt;script&gt;alert('bad')&lt;/script&gt;

    if ``strip=True``, bleach will output:

        alert('bad')

    But we want to strip both the tag and contents for certain tags like script
    and style.  This subclass does that.

    Also support data URI's.
    """
    allowed_elements = bleach_whitelist.markdown_tags
    allowed_attributes = bleach_whitelist.markdown_attrs
    suppressed_elements = ["script", "style"]
    strip_disallowed_elements = True
    strip_html_comments = True

    def __init__(self, *args, **kwargs):
        self.suppressing = None
        super(Sanitizer, self).__init__(*args, **kwargs)

    def sanitize_token(self, token):
        extra_data = []
        # Allow data URIs of some types for images. Store them in 'extra_data'
        # so we can appendthem to the result.
        if token.get('name') == "img":
            for (name, val) in token['data']:
                if name == u"src":
                    if re.match("^data:image/(png|gif|jpeg);base64,[A-Za-z0-9+/=]+$", val):
                        extra_data.append((name, val))
                    break
        # Do sanitization on the parent.
        result = super(Sanitizer, self).sanitize_token(token)
        # Append extra data potentially including data URI's.
        if extra_data:
            if result['data']:
                result['data'] += extra_data
            else:
                result['data'] = extra_data
        print result

        # Suppress elements like script and style entirely.
        if token.get('name') and token['name'] in self.suppressed_elements:
            if token['type'] == tokenTypes['StartTag']:
                self.suppressing = token['name']
            elif token['type'] == tokenTypes['EndTag'] and token['name'] == self.suppressing:
                self.suppressing = False
        if self.suppressing:
            return {u'data': '', 'type': 2}
        else:
            return result

def sanitize_html(raw_html):
    """
    Sanitize the given raw_html.
    """
    # Strip tags to the few that we like
    parser = html5lib.HTMLParser(tokenizer=Sanitizer)
    clean = _render(parser.parseFragment(raw_html))

#    walker = html5lib.treewalkers.getTreeWalker('etree')
#    stream = walker(parser.parseFragment(raw_html))
#    serializer = html5lib.serializer.HTMLSerializer(quote_attr_values=False, omit_optional_tags=False)
#    print unicode(serializer.render(stream))

    # Set anchor tags' targets
    clean = bleach.linkify(clean, callbacks=[
        bleach.callbacks.nofollow,
        bleach.callbacks.target_blank
    ])
    return clean

def set_canonical_rel(raw_html, href):
    """
    Add or update <link rel='canonical'...> in the given html to the given
    href. Note that this has the side effect of appending html/head/body tags
    to the given html fragment if it doesn't already have them.
    """
    soup = BeautifulSoup(raw_html)
    canonical_tags = soup.find_all(_canonical_link_predicate)
    if canonical_tags:
        for tag in canonical_tags:
            tag['href'] = href
    else:
        new_tag = soup.new_tag('link', rel='canonical', href=href)
        head = soup.find('head')
        head.append(new_tag)
    return unicode(soup)
