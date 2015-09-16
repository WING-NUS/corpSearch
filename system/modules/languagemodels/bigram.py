import cPickle

from .. import BaseFeature
from vocab.languagemodel import BigramLanguageModel


class DescriptionLanguageModel(BaseFeature):
    @staticmethod
    def feature_labels():
        return [
            'Probability: Description belongs to Official LM',
            'Probability: Description belongs to Affiliate LM',
            'Probability: Description belongs to Unrelated LM'
        ]

    @staticmethod
    def score(query, profile, data=None):
        if data is None:
            raise Exception('Description Language Models weren\'t passed.')

        lowered_description = profile.description.lower()

        correct_bigram_LM = data['correct_bigram_LM']
        probability_description_correct = correct_bigram_LM.probability(
            lowered_description)

        affiliate_bigram_LM = data['affiliate_bigram_LM']
        probability_description_affiliate = affiliate_bigram_LM.probability(
            lowered_description)

        incorrect_bigram_LM = data['incorrect_bigram_LM']
        probability_description_incorrect = incorrect_bigram_LM.probability(
            lowered_description)

        return [
            probability_description_correct,
            probability_description_affiliate,
            probability_description_incorrect
        ]

    @staticmethod
    def preprocess(profiles, network_name):
        for label in profiles.iterkeys():
            model = BigramLanguageModel()

            for profile in profiles[label]:
                model.add(profile.description.lower())

            model.prune()
            with open(network_name + 'BigramLM-' + label, 'wb') as output:
                cPickle.dump(model, output)

    @staticmethod
    def retrieve_preprocessed_data(network_name):
        labels = ['correct', 'affiliate', 'incorrect']

        data = {}
        for label in labels:
            with open(network_name + 'BigramLM-' + label, 'rb') as input_file:
                model = cPickle.load(input_file)
                data[label + '_bigram_LM'] = model

        return data


class PostContentLanguageModel(BaseFeature):
    @staticmethod
    def feature_labels():
        return [
            'Probability: Post Content belongs to Official LM',
            'Probability: Post Content belongs to Affiliate LM',
            'Probability: Post Content belongs to Unrelated LM'
        ]

    @staticmethod
    def score(query, profile, data=None):
        if data is None:
            raise Exception('Post Content Language Models weren\'t passed.')

        correct_post_bigram_LM = data['correct_post_bigram_LM']
        affiliate_post_bigram_LM = data['affiliate_post_bigram_LM']
        incorrect_post_bigram_LM = data['incorrect_post_bigram_LM']

        probability_posts_correct = -1 if not len(profile.posts) else 0
        probability_posts_affiliate = -1 if not len(profile.posts) else 0
        probability_posts_incorrect = -1 if not len(profile.posts) else 0

        if len(profile.posts):
            for post in (x.content.lower() for x in profile.posts):
                probability_posts_correct += (
                    correct_post_bigram_LM.probability(post))

                probability_posts_affiliate += (
                    affiliate_post_bigram_LM.probability(post))

                probability_posts_incorrect += (
                    incorrect_post_bigram_LM.probability(post))

        return [
            probability_posts_correct,
            probability_posts_affiliate,
            probability_posts_incorrect
        ]

    @staticmethod
    def preprocess(profiles, network_name):
        for label in profiles.iterkeys():
            model = BigramLanguageModel()

            for profile in profiles[label]:
                for post in (x.content.lower() for x in profile.posts):
                    model.add(post)

            model.prune()
            with open(network_name + 'PostBigramLM-' + label, 'wb') as output:
                cPickle.dump(model, output)

    @staticmethod
    def retrieve_preprocessed_data(network_name):
        labels = ['correct', 'affiliate', 'incorrect']

        data = {}
        for label in labels:
            with open(network_name + 'PostBigramLM-' + label,
                      'rb') as input_file:
                model = cPickle.load(input_file)
                data[label + '_post_bigram_LM'] = model

        return data
