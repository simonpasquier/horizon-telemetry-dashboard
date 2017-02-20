from __future__ import absolute_import

import collections
import functools
from datetime import datetime, timedelta

from django.conf import settings

CACHE_EXPIRATION = getattr(settings, 'CACHE_EXPIRATION', 60)


CachedItem = collections.namedtuple('CachedItem', 'value', 'timestamp')

class memoized(object):
    """Decorator caching the return value until it expires.

    If called later with the same arguments, the cached value is returned
    (not reevaluated) until the expiration period has elapsed.
    """

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def is_valid(self, _id):
        expired_time = datetime.now() - timedelta(seconds=CACHE_EXPIRATION)
        return _id in self.cache and \
            self.cache[_id].timestamp + timedelta(seconds=CACHE_EXPIRATION) < datetime.now()

    def __call__(self, *args):
        # use the first function argument as cache ID
        _id = args[0]
        if not self.is_valid(_id):
            v = self.func(*args)
            self.cache[_id].timestamp = datetime.now()
            self.cache[_id].value = v

        return self.cache[_id].value

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)
