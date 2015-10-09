from .. import BaseFeature
from distance import NormalizedEditDistance


class NormalizedEditDistanceQueryToHandle(BaseFeature):
    """The normalized edit distance between the query and the handle."""
    @staticmethod
    def feature_labels():
        return [
            'Normalized Edit Distance: Query to Handle'
        ]

    @staticmethod
    def score(query, profile, data=None):
        return [NormalizedEditDistance.between(query, profile.handle)]


class NormalizedEditDistanceQueryToDisplayName(BaseFeature):
    """The normalized edit distance between the query and the display name."""
    @staticmethod
    def feature_labels():
        return [
            'Normalized Edit Distance: Query to Display Name'
        ]

    @staticmethod
    def score(query, profile, data=None):
        return [NormalizedEditDistance.between(query, profile.display_name)]
