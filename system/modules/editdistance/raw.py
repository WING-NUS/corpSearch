from .. import BaseFeature
from distance import EditDistance


class EditDistanceQueryToHandle(BaseFeature):
    """The raw edit distance between the query and the handle."""
    @staticmethod
    def feature_labels():
        return [
            'Edit Distance: Query to Handle'
        ]

    @staticmethod
    def score(query, profile, data=None):
        return [EditDistance.between(query, profile.handle)]


class EditDistanceQueryToDisplayName(BaseFeature):
    """The raw edit distance between the query and the display name."""
    @staticmethod
    def feature_labels():
        return [
            'Edit Distance: Query to Display Name'
        ]

    @staticmethod
    def score(query, profile, data=None):
        return [EditDistance.between(query, profile.display_name)]
