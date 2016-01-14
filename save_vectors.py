from __future__ import print_function
import itertools

from trainer.trainer import get_twitter_entries, get_facebook_entries,\
                            Trainer
from trainer.social_profile import TwitterProfile, FacebookProfile
from system.systems import Final


def get_feature_vectors(network_name, entries, profile_type):
    network_trainer = Trainer(entries, profile_type, Final, network_name)
    training_set = network_trainer.generate_training_set()

    vectors = training_set.data
    labels = training_set.labels

    joined_vectors = [{
        'vector': vector,
        'label': label
    } for vector, label in itertools.izip(vectors, labels)]

    return joined_vectors

def feature_vector_to_line(joined_vector):
    # Format:
    # (class label) (feature ID):(its value) (feature ID):(its value)
    # eg. 1 1:23 2:3 3:5.2 ... 14:0.232
    vector = joined_vector['vector']
    label = joined_vector['label']

    components = []
    components.append(str(label))

    for index, value in enumerate(vector):
        components.append(str(index+1)+':{0:.6f}'.format(value))

    return ' '.join(components)

def write_lines_to_file(lines, file_name):
    with open(file_name, 'w+') as output_file:
        for line in lines:
            output_file.write(line)
            output_file.write('\n')

def main():
    print('Twitter.')
    twitter_vectors = get_feature_vectors('twitter', get_twitter_entries(),
                                          TwitterProfile)
    twitter_lines = (feature_vector_to_line(x) for x in twitter_vectors)
    write_lines_to_file(twitter_lines, 'twitter vectors.txt')

    print('Facebook.')
    facebook_vectors = get_feature_vectors('facebook', get_facebook_entries(),
                                           FacebookProfile)
    facebook_lines = (feature_vector_to_line(x) for x in facebook_vectors)
    write_lines_to_file(facebook_lines, 'facebook vectors.txt')

if __name__ == '__main__':
    main()
