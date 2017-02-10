
from __future__ import absolute_import

import functools
from django.conf import settings
from datetime import datetime, timedelta

CACHE_EXPIRATION = getattr(settings, 'CACHE_EXPIRATION', 60)


class memoized(object):

    """Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated), unless more than expiration passed.
    """

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def is_actual(self, id):
        expirated = datetime.now() - timedelta(seconds=CACHE_EXPIRATION)
        if id in self.cache \
                and self.cache[id][0] >= expirated:
            return True
        return False

    def __call__(self, *args):
        
        # gets first function argument as cache ID
        # for example ctl01 will be cache ID
        id = args[0]
        if self.is_actual(id):
            return self.cache[id][1]
        else:
            print "Now we call graphite for {}".format(id)
            content = self.func(*args)
            self.cache[id] = datetime.now(), content
            return content

    def __repr__(self):
        '''Return the function's docstring.'''
        return self.func.__doc__

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return functools.partial(self.__call__, obj)
