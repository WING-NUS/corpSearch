class CorpSearchSystem(object):
    def __init__(self, name, features):
        self.name = name
        self.features = features

        self.labels = []
        for feature in self.features:
            self.labels += feature.feature_labels()

    def feature_vector_labels(self):
        return self.labels

    def convert_to_feature_vector(self, query, profile, data=None):
        vector = []

        for feature in self.features:
            vector += feature.score(query=query, profile=profile, data=data)

        return vector

    def preprocess(self, profiles, network_name):
        for feature in self.features:
            feature.preprocess(profiles, network_name)

    def retrieve_preprocessed_data(self, network_name):
        data = {}
        for feature in self.features:
            feature_data = feature.retrieve_preprocessed_data(network_name)
            if feature_data is not None:
                data.update(feature_data)

        return data
