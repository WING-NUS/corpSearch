from time import time
import shelve
import os
import os.path
import functools

from pymongo import DESCENDING

import mongo

def cache(filename):
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
    if not os.path.exists('cache'):
        os.mkdir('cache')


@expiring_cache('fibonacci', 600)
def fibonacci(n):
    if n == 0 or n == 1:
        return 1

    return fibonacci(n - 1) + fibonacci(n - 2)
