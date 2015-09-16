from sklearn.externals import joblib

from companyscorer.classifier import NetworkClassifier
from companyscorer.searchengines import TwitterSearch, FacebookSearch
import config


class SingleNetworkSearcher(object):
    """Handles searching for a company's profiles on an individual social network."""

    def __init__(self, classifier, searchengine, profile_converter, network):
        self.engine = searchengine
        self.classifier = NetworkClassifier(classifier, profile_converter,
                                            network)
        self.network = network

    def query(self, query):
        """Returns results for this searcher's network."""
        profiles = self.engine.query(query)
        classified = self.classifier.classify_profiles(name=query,
                                                       profiles=profiles)

        return classified


class TwitterSearcher(object):
    def __init__(self):
        self.engine = SingleNetworkSearcher(
            classifier=joblib.load('twitter_classifier.pkl'),
            searchengine=TwitterSearch(),
            profile_converter=config.converter,
            network='twitter'
        )

    def query(self, query):
        return self.engine.query(query)


class FacebookSearcher(object):
    def __init__(self):
        self.engine = SingleNetworkSearcher(
            classifier=joblib.load('facebook_classifier.pkl'),
            searchengine=FacebookSearch(),
            profile_converter=config.converter,
            network='facebook'
        )

    def query(self, query):
        return self.engine.query(query)
