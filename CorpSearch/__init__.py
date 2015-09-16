from tornado.web import RequestHandler, Application

from searcher import TwitterSearcher, FacebookSearcher
from duckduckdescription import DuckDuckDescription


twitter_searcher = TwitterSearcher()
facebook_searcher = FacebookSearcher()


class DuckDuckGoDescriptionHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def get(self, name):
        if not name:
            self.write({})
            self.finish()

        ddg_result = DuckDuckDescription.query(name)
        if ddg_result:
            self.write({
                'name': ddg_result['name'],
                'description': ddg_result['description']
            })
            self.finish()
            return

        self.write({})
        self.finish()


class TwitterResultHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def get(self, name):
        if not name:
            self.write({})
            self.finish()
            return

        results = twitter_searcher.query(name)

        self.write(create_results_dict(results))
        self.finish()


class FacebookResultHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def get(self, name):
        if not name:
            self.write({})
            self.finish
            return

        results = facebook_searcher.query(name)

        self.write(create_results_dict(results))
        self.finish()

app = Application([
    (r'/company/(.*)/description', DuckDuckGoDescriptionHandler),
    (r'/company/(.*)/twitter', TwitterResultHandler),
    (r'/company/(.*)/facebook', FacebookResultHandler)
])

def create_results_dict(results):
    official = [{
            'profile': result['profile'].to_dict(),
            'probability': result['probability'],
            'vector': result['vector'],
            'vectorLabels': results.features
        } for result in results.official]

    affiliate = [{
        'profile': result['profile'].to_dict(),
        'probability': result['probability'],
        'vector': result['vector'],
        'vectorLabels': results.features
    } for result in results.affiliate]

    unrelated = [{
            'profile': result['profile'].to_dict(),
            'probability': result['probability'],
            'vector': result['vector'],
            'vectorLabels': results.features
    } for result in results.unrelated]

    return {
        'belonging': official,
        'affiliate': affiliate,
        'notBelonging': unrelated
    }
