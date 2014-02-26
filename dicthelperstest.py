# I need to turn this into a proper unit test.
# uhm, this is horrible. sorry everybody.
# -Bryan

import time
from dicthelpers import fallbackdict

start = time.time()

fallback = {1: '1'}
poop = fallbackdict(fallback)
print 'expect 1 (fallback): ' + poop[1]
fallback[2] = '2'
print 'expect 2 (dynamic fallback): ' + poop[2]
poop[2] = '3'
print 'expect 3 (overridden): ' + poop[2]
del poop[2]
print 'expect 2 (fallback after delete): ' + poop[2]
fallback['three'] = 3
fallback[3] = '3{three}'
print 'expect 33 (formatting): ' + poop[3]
print 'expect 4 (len): ' + str(len(poop))
fallback['infinite'] = '{infinite}'
print 'simple infinite recursion test: ' + poop['infinite']
fallback['infone'] = '{inftwo}'
fallback['inftwo'] = '{infone}'
print 'double infinite recursion test: ' + poop['infone']
fallback['2infone'] = '{2inftwo}'
fallback['2inftwo'] = '{2infone}'
print 'double infinite recursion test: ' + poop['2inftwo']
poop['four'] = 4
poop[4] = '4{four}'
print 'expect 34 (self as string mapping): {three}{four}'.format(**poop)
print 'expect 44 (self formatting): ' + poop[4]
# silent iter length processing.
# this used to take 1 or 2 seconds prior to optimizations
for x in poop: poop[x]

stop = time.time()
print "execution " + str(stop - start)
