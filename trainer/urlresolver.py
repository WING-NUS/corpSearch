from simplediskcache.SimpleDiskCache import cache

import requests
import tldextract


class UrlResolver(object):
    """Resolves shortened URLs and finds their final destination."""

    @staticmethod
    @cache('urls')
    def resolve_shortened_url(url):
        """Returns the final destination of a shortened URL. This is done by
        making a request to it."""
        try:
            request = requests.get(url, timeout=5)
            resolved_url = request.url
            return resolved_url
        except (requests.ConnectionError, requests.exceptions.Timeout) as e:
            return e.request.url

    @staticmethod
    def get_domain_for_url(url):
        """Returns the domain of a given URL."""
        domain = tldextract.extract(url).domain

        return domain
