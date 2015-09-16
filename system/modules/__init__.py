class BaseFeature(object):
    """Dummy base feature that provides empty methods which do nothing when
    called. All features inherit from this."""

    @staticmethod
    def feature_labels():
        """Should return a list of strings corresponding to each score
        in the feature's sub-vector."""
        return []

    @staticmethod
    def score(query, profile, data=None):
        """Should return a list of scores for a given profile and query."""
        return []

    @staticmethod
    def preprocess(profiles, network_name):
        """Preprocessing of all profiles. profiles is a dictionary keyed by
        class, with value being the list of profiles in that class."""
        pass

    @staticmethod
    def retrieve_preprocessed_data(network_name):
        """Retrieve the preprocessed data from wherever it's stored."""
        return None
