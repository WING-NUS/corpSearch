from .. import BaseFeature


class OccurrencesOfQueryInDescCaseSensitive(BaseFeature):
    """The amount of times the query appears in the profile's description,
    taking case into account."""
    @staticmethod
    def feature_labels():
        return [
            'Occurrences of Query in Description (Case Sensitive)'
        ]

    @staticmethod
    def score(query, profile, data=None):
        return [profile.description.count(query)]


class OccurrencesOfQueryInDescCaseInsensitive(BaseFeature):
    """The amount of times the query appears in the profile's description,
    ignoring case."""
    @staticmethod
    def feature_labels():
        return [
            'Occurrences of Query in Description (Case Sensitive)'
        ]

    @staticmethod
    def score(query, profile, data=None):
        return [profile.description.lower().count(query.lower())]
