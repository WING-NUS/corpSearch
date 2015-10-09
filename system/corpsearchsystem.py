class CorpSearchSystem(object):
    """Defines a system consisting of a set of features that convert
    profiles into vectors. This can be used to easily specify different
    sets of features to be used in classification."""
    def __init__(self, name, features):
        self.name = name
        self.features = features

        self.labels = []
        for feature in self.features:
            self.labels += feature.feature_labels()

    def feature_vector_labels(self):
        """Returns the list of labels for each field in the vector."""
        return self.labels

    def convert_to_feature_vector(self, query, profile, data=None):
        """Given a query, a social network profile, and optionally some common
        data, converts the profile to a vector for classification."""
        vector = []

        for feature in self.features:
            vector += feature.score(query=query, profile=profile, data=data)

        return vector

    def preprocess(self, profiles, network_name):
        """Given a series of profiles and the name of a social network,
        provides the profiles to each feature for preprocessing."""
        for feature in self.features:
            feature.preprocess(profiles, network_name)

    def retrieve_preprocessed_data(self, network_name):
        """Given the name of a social network, retrieves the preprocessed
        data for that network from all features."""
        data = {}
        for feature in self.features:
            feature_data = feature.retrieve_preprocessed_data(network_name)
            if feature_data is not None:
                data.update(feature_data)

        return data
