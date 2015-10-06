from itertools import izip
from collections import namedtuple

ClassificationResult = namedtuple('ClassificationResult',
                                  ['company_name',
                                   'official',
                                   'unrelated',
                                   'affiliate',
                                   'features'])


class NetworkClassifier(object):
    """Classifies profiles for a given network as belonging to a particular
    company or not."""
    def __init__(self, classifier, profile_converter, network):
        self.classifier = classifier
        self.profile_converter = profile_converter
        self.network = network

    def classify_profiles(self, name, profiles):
        """Given the name of a company and an enumerable of profiles,
        returns a classification result for that enumerable."""

        feature_list = self.profile_converter.feature_vector_labels()
        if not len(profiles):
            return ClassificationResult(company_name=name,
                                        official=[],
                                        affiliate=[],
                                        unrelated=[],
                                        features=feature_list)

        official = []
        affiliate = []
        unrelated = []

        preprocessed_data = self.profile_converter.retrieve_preprocessed_data(
            self.network)
        feature_vectors = [self.profile_converter.convert_to_feature_vector(
                            name, x, data=preprocessed_data)
                           for x in profiles]

        predicted_probabilities = self.classifier.predict_proba(feature_vectors)
        predicted_classes = self.classifier.predict(feature_vectors)

        for prediction in izip(predicted_probabilities,
                               profiles,
                               feature_vectors,
                               predicted_classes):
            profile_predicted_official = prediction[3] == 2
            profile_predicted_affiliate = prediction[3] == 1
            profile = prediction[1]
            vector = prediction[2]

            if profile_predicted_official:
                official.append({
                    'profile': profile,
                    'probability': prediction[0][2],
                    'vector': vector
                })
            elif profile_predicted_affiliate:
                affiliate.append({
                    'profile': profile,
                    'probability': prediction[0][1],
                    'vector': vector
                })
            else:
                unrelated.append({
                    'profile': profile,
                    'probability': prediction[0][0],
                    'vector': vector
                })

        # We sort belonging in descending order of probability, but not-belonging
        # in ascending order. This is because profiles which we're not entirely
        # sure don't belong are more interesting than the ones that definitely don't.
        official = sorted(official, reverse=True,
                          key=lambda x: x['probability'])
        affiliate = sorted(affiliate, reverse=True,
                           key=lambda x: x['probability'])
        unrelated = sorted(unrelated, key=lambda x: x['probability'])

        result = ClassificationResult(
            company_name=name,
            official=official,
            unrelated=unrelated,
            affiliate=affiliate,
            features=feature_list)
        return result
