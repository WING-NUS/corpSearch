from .. import BaseFeature


class LengthOfQuery(BaseFeature):
    @staticmethod
    def feature_labels():
        return [
            'Length of Query'
        ]

    @staticmethod
    def score(query, profile, data=None):
        return [len(query)]


class LengthOfHandle(BaseFeature):
    @staticmethod
    def feature_labels():
        return [
            'Length of Handle'
        ]

    @staticmethod
    def score(query, profile, data=None):
        return [len(profile.handle)]


class LengthOfDisplayName(BaseFeature):
    @staticmethod
    def feature_labels():
        return [
            'Length of Display Name'
        ]

    @staticmethod
    def score(query, profile, data=None):
        return [len(profile.display_name)]
