from collections import namedtuple

from sklearn.externals import joblib

from social_profile import FacebookProfile, TwitterProfile
import itertools

import config
import mongo

training_set = namedtuple('TrainingSet', ['data', 'labels'])


class Trainer(object):
    """Trains a classifier for a particular social network."""
    def __init__(self, db_profiles, profile_type, profile_converter, network):
        self.db_profiles = db_profiles
        self.profile_type = profile_type
        self.profile_converter = profile_converter
        self.network = network

    def generate_training_set(self):
        """Returns a training set for the profiles used to initialize this
        Trainer. The training set is a named tuple with two properties:

            `data`: A list of feature vectors, each of which corresponds to a
            social network profile.

            `labels`: A list of numerical labels.

        The indexes in both `data` and `labels` are identical - i.e. vector n
        in `data` corresponds to label n in `labels`."""
        profiles = list(self.db_profiles)
        feature_vectors = []
        labels = []

        correct_names = [x['name'] for x in profiles if x['label'] == 2]
        correct_profiles = [self.profile_type(x['profile'], x['posts'])
                            for x in profiles if x['label'] == 2]

        affiliate_names = [x['name'] for x in profiles if x['label'] == 1]
        affiliate_profiles = [self.profile_type(x['profile'], x['posts'])
                              for x in profiles if x['label'] == 1]

        incorrect_names = [x['name'] for x in profiles if x['label'] == 0]
        incorrect_profiles = [self.profile_type(x['profile'], x['posts'])
                              for x in profiles if x['label'] == 0]

        profiles = {
            'correct': correct_profiles,
            'affiliate': affiliate_profiles,
            'incorrect': incorrect_profiles
        }
        self.profile_converter.preprocess(profiles, self.network)
        data = self.profile_converter.retrieve_preprocessed_data(self.network)

        for name, profile in itertools.izip(correct_names, correct_profiles):
            features = self.profile_converter.convert_to_feature_vector(
                name, profile, data=data)

            feature_vectors.append(features)
            labels.append(2)

        for name, profile in itertools.izip(affiliate_names,
                                            affiliate_profiles):
            features = self.profile_converter.convert_to_feature_vector(
                name, profile, data=data)

            feature_vectors.append(features)
            labels.append(1)

        for name, profile in itertools.izip(incorrect_names,
                                            incorrect_profiles):
            features = self.profile_converter.convert_to_feature_vector(
                name, profile, data=data)

            feature_vectors.append(features)
            labels.append(0)

        return training_set(data=feature_vectors, labels=labels)

    def train_classifier(self, classifier, training_set):
        """Given an initialized scikit-learn classifier and a training set,
        trains the classifier and returns it."""
        classifier.fit(training_set.data, training_set.labels)
        return classifier


def train_twitter(classifier):
    """Helper method to train an initialized scikit-learn classifier on
    all Twitter profiles."""
    all_entries = get_twitter_entries()

    twitter_trainer = Trainer(all_entries, TwitterProfile, config.converter,
                              'twitter')
    training_set = twitter_trainer.generate_training_set()

    trained_classifier = twitter_trainer.train_classifier(classifier,
                                                          training_set)

    return trained_classifier


def train_facebook(classifier):
    """Helper method to train an initialized scikit-learn classifier on
    all Facebook profiles."""
    all_entries = get_facebook_entries()

    facebook_trainer = Trainer(all_entries, FacebookProfile, config.converter,
                               'facebook')
    training_set = facebook_trainer.generate_training_set()

    trained_classifier = facebook_trainer.train_classifier(classifier,
                                                           training_set)

    return trained_classifier


def get_twitter_entries():
    """Connects to MongoDB and returns all Twitter profiles with their
    labels."""
    client = mongo.client
    labels = client.labels.twitter
    profiles = client.searchresults.twitterProfiles
    posts = client.posts.twitter

    labelled_entries = get_labelled_entries(labels, profiles)
    for entry in labelled_entries:
        profile_id = entry['profile']['id']

        if entry['profile']['protected']:
            entry['posts'] = []
        else:
            retrieved_posts = [x['post'] for x in posts.find({'user': profile_id})]

            # TODO: move these to a separate script.
            # if not len(retrieved_posts):
            #     retrieved_posts = twittersearch.posts_for(profile_id)
            #     for post in retrieved_posts:
            #         posts.insert({
            #                      'user': profile_id,
            #                      'post': post
            #                      })
            entry['posts'] = retrieved_posts

    return labelled_entries


def get_facebook_entries():
    """Connects to MongoDB and returns all Facebook profiles with their
    labels."""
    client = mongo.client
    labels = client.labels.facebook
    profiles = client.searchresults.facebookProfiles
    posts = client.posts.facebook

    labelled_entries = get_labelled_entries(labels, profiles)
    for entry in labelled_entries:
        profile_id = entry['profile']['id']

        retrieved_posts = [x['post'] for x in posts.find({'user': profile_id})]

        # TODO: move these to a separate script.
        # if not len(retrieved_posts):
        #     retrieved_posts = facebooksearch.posts_for(profile_id)
        #     for post in retrieved_posts:
        #         if 'message' in post or 'description' in post:
        #             posts.insert({
        #                          'user': profile_id,
        #                          'post': post
        #                          })
        entry['posts'] = retrieved_posts

    return labelled_entries


def get_labelled_entries(labels, profiles):
    """Given the pymongo collections for some social network profiles and their
    labels, returns a list of dictionaries containing:

        `name`: the name of the company the profile is labelled relative to.

        `profile`: the profile itself.

        `label`: the label of this profile, relative to the company."""
    # We need to return entries in the form:
    # {
    #   'name': <query>,
    #   'profile': <profile>,
    #   'label': <label>
    # }

    all_entries = []
    for record in labels.find():
        entry = {
            'name': record['query'],
            'label': record['label'],
            'profile': profiles.find_one({'_id': record['profile']})
        }

        all_entries.append(entry)

    return all_entries


if __name__ == '__main__':
    twitter_classifier = train_twitter(config.twitter_classifier)
    joblib.dump(twitter_classifier, 'twitter_classifier.pkl')

    facebook_classifier = train_facebook(config.facebook_classifier)
    joblib.dump(facebook_classifier, 'facebook_classifier.pkl')
