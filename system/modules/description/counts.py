from .. import BaseFeature


class OccurrencesOfQueryInDescCaseSensitive(BaseFeature):
    @staticmethod
    def feature_labels():
        return [
            'Occurrences of Query in Description (Case Sensitive)'
        ]

    @staticmethod
    def score(query, profile, data=None):
        return [profile.description.count(query)]


class OccurrencesOfQueryInDescCaseInsensitive(BaseFeature):
    @staticmethod
    def feature_labels():
        return [
            'Occurrences of Query in Description (Case Sensitive)'
        ]

    @staticmethod
    def score(query, profile, data=None):
        return [profile.description.lower().count(query.lower())]
