from time import time
import shelve
import os
import os.path
import functools

from pymongo import DESCENDING

import mongo

def cache(filename):
    """Decorator that implements a file-based cache for the given method."""
    def wrapper(func):
        @functools.wraps(func)
        def cacher(*args, **kwargs):
            ensure_cache_dir_exists()

            path = os.path.join('cache', filename)
            store = shelve.open(path)

            key = str(args) + str(kwargs)

            if key in store:
                return store[key]['value']

            now = time()

            store[key] = {
                'time': now,
                'value': func(*args, **kwargs)
            }

            value = store[key]['value']
            store.close()

            return value

        return cacher

    return wrapper


def expiring_cache(filename, time_in_seconds):
    """Decorator that implements a MongoDB-based expiring cache
    for the given function. If the result stored in the DB is >
    time_in_seconds old, the function is invoked, and the result
    stored and returned."""
    def wrapper(func):
        @functools.wraps(func)
        def cacher(*args, **kwargs):
            now = time()

            client = mongo.client
            db = client.cache[filename]
            key = str(args) + str(kwargs)

            latest = db.find({'key': key}).sort("time", DESCENDING)
            if latest.count():
                saved = latest[0]
                value_has_expired = now - saved['time'] > time_in_seconds
                if not value_has_expired:
                    return saved['value']

            entry = {
                'time': now,
                'key': key,
                'value': func(*args, **kwargs)
            }

            db.insert(entry)
            return entry['value']

        return cacher

    return wrapper


def ensure_cache_dir_exists():
    """Creates the cache directory if it does not already exist."""
    if not os.path.exists('cache'):
        os.mkdir('cache')


@expiring_cache('fibonacci', 600)
def fibonacci(n):
    """Demo method for the expiring cache. Calculates
    the n-th fibonacci number, with results expiring
    after ten minutes."""
    if n == 0 or n == 1:
        return 1

    return fibonacci(n - 1) + fibonacci(n - 2)
