import requests
from simplediskcache.SimpleDiskCache import expiring_cache


class DuckDuckDescription(object):
    """Searches DuckDuckGo for a company, and returns
    instant answer information for that company."""

    @staticmethod
    @expiring_cache('ddg', 60*60*24*90)
    def query(company):
        """Searches the DuckDuckGo Instant Answer API for ``company``
        and returns a description for it."""
        query_params = {
            'q': company,
            'format': 'json',
            'skip_disambig': 1,
            't': 'CorpSearch'
        }

        r = requests.get('https://api.duckduckgo.com/',
                         params=query_params)

        if r.text == '':
            import pdb; pdb.set_trace()

        response = r.json()

        if response['Entity'] == 'company':
            return {
                'name': response['Heading'],
                'description': {
                    'text': response['AbstractText'],
                    'source': response['AbstractSource'],
                    'link': response['AbstractURL']
                }
            }

        return None
