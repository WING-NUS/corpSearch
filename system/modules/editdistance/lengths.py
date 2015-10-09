from .. import BaseFeature


class LengthOfQuery(BaseFeature):
    """The length of the query, in characters."""
    @staticmethod
    def feature_labels():
        return [
            'Length of Query'
        ]

    @staticmethod
    def score(query, profile, data=None):
        return [len(query)]


class LengthOfHandle(BaseFeature):
    """The length of the handle, in characters."""
    @staticmethod
    def feature_labels():
        return [
            'Length of Handle'
        ]

    @staticmethod
    def score(query, profile, data=None):
        return [len(profile.handle)]


class LengthOfDisplayName(BaseFeature):
    """The length of the display name, in characters."""
    @staticmethod
    def feature_labels():
        return [
            'Length of Display Name'
        ]

    @staticmethod
    def score(query, profile, data=None):
        return [len(profile.display_name)]
