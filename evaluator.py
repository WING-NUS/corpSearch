from collections import defaultdict
import multiprocessing
import itertools
import time
import argparse
import cPickle
import os.path

from pathos.multiprocessing import ProcessingPool
from sklearn import cross_validation
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB, BernoulliNB, MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
import numpy

from trainer.trainer import Trainer, get_facebook_entries, get_twitter_entries
from trainer.social_profile import TwitterProfile, FacebookProfile
from corpsearch.searcher import SingleNetworkSearcher
from corpsearch.companyscorer.searchengines import TwitterSearch,\
                                                   FacebookSearch
from trainer.converters import all_converters
import config


class MaxValue(object):
    """Helper class to find a maximum value out of a series of
    numbers."""
    def __init__(self):
        self.value = None

    def update(self, value):
        """Updates the internally-stored value if the given value is larger."""
        if self.value < value:
            self.value = value


class SystemEvaluationResult(object):
    def __init__(self, classifier_results):
        self.official_max = defaultdict(MaxValue)
        self.affiliate_max = defaultdict(MaxValue)

        self.official_metrics = defaultdict(dict)
        self.affiliate_metrics = defaultdict(dict)

        self.process_classifier_results(classifier_results)

    def process_classifier_results(self, results):
        for classifier, fold_results in results.iteritems():
            self.process_official_results(
                results=[x['official'] for x in fold_results],
                classifier_name=classifier)

            self.process_affiliate_results(
                results=[x['affiliate'] for x in fold_results],
                classifier_name=classifier)

    def process(self):
        return {
            'official': self.__get_returnable_dict_for_class(
                store=self.official_metrics,
                maximums=self.official_max),
            'affiliate': self.__get_returnable_dict_for_class(
                store=self.affiliate_metrics,
                maximums=self.affiliate_max)
        }

    def process_official_results(self, results, classifier_name):
        summarized = MetricCalculator.overall_metrics(results)

        self.__store_classifier_metrics(self.official_metrics, summarized,
                                        classifier_name)
        self.__update_maximums(self.official_max, summarized)

    def process_affiliate_results(self, results, classifier_name):
        summarized = MetricCalculator.overall_metrics(results)

        self.__store_classifier_metrics(self.affiliate_metrics, summarized,
                                        classifier_name)
        self.__update_maximums(self.affiliate_max, summarized)

    def __store_classifier_metrics(self, store, results, classifier_name):
        store['f1'][classifier_name] = results['macro_average_f1']
        store['precision'][classifier_name] = results['macro_average_precision']
        store['recall'][classifier_name] = results['macro_average_recall']

    def __update_maximums(self, store, results):
        store['f1'].update(results['max_f1'])
        store['precision'].update(results['max_precision'])
        store['recall'].update(results['max_recall'])

    def __get_returnable_dict_for_class(self, store, maximums):
        processed = {
            'f1': store['f1'],
            'precision': store['precision'],
            'recall': store['recall']
        }

        processed['f1']['max'] = maximums['f1'].value
        processed['precision']['max'] = maximums['precision'].value
        processed['recall']['max'] = maximums['recall'].value

        return processed


class Evaluator(object):
    """Evaluates a classifier for a particular social network."""
    def __init__(self, db_profiles, profile_type, search_engine, network,
                 converter=config.evaluate_converter):
        self.db_profiles = db_profiles
        self.profile_type = profile_type
        self.search_engine = search_engine
        self.network = network
        self.converter = converter

    @property
    def profiles(self):
        self.db_profiles, clone = itertools.tee(self.db_profiles)
        return clone

    def evaluate(self):
        trainer = Trainer(self.profiles, self.profile_type,
                          self.converter, self.network)
        training_set = trainer.generate_training_set()

        profiles = numpy.array(list(self.profiles))
        data = numpy.array(training_set.data)
        labels = numpy.array(training_set.labels)

        fold_iterator = cross_validation.StratifiedKFold(labels,
                                                         n_folds=10,
                                                         shuffle=True,
                                                         random_state=42)

        official_profile_pairs = ((x['name'], self.profile_type(x['profile'],
                                                                x['posts']))
                                  for x in self.profiles if x['label'] == 2)
        affiliate_profile_pairs = ((x['name'], self.profile_type(x['profile'],
                                                                 x['posts']))
                                   for x in self.profiles if x['label'] == 1)

        official_profiles = defaultdict(list)
        for name, profile in official_profile_pairs:
            official_profiles[name].append(profile)

        affiliate_profiles = defaultdict(list)
        for name, profile in affiliate_profile_pairs:
            affiliate_profiles[name].append(profile)

        classification_results = defaultdict(list)
        fold = 1
        for train, test in fold_iterator:
            classifiers = initialize_classifiers()

            training_data = data[train]
            training_labels = labels[train]

            test_set = itertools.compress(profiles[test], labels[test])
            company_names = set(x['name'] for x in test_set)
            print 'Test set', fold, '-', len(company_names), 'companies.'

            for classifier in classifiers:
                classifier_name = classifier['type']
                c = classifier['classifier']
                trained = c.fit(training_data, training_labels)

                system = SingleNetworkSearcher(
                    classifier=trained,
                    searchengine=self.search_engine,
                    profile_converter=self.converter,
                    network=self.network)

                number_of_workers = int(multiprocessing.cpu_count() * 0.75)
                worker_pool = ProcessingPool(number_of_workers)
                all_results = worker_pool.map(system.query, company_names)

                combined_official_results = []
                combined_affiliate_results = []
                for idx, name in enumerate(company_names):
                    official_results = official_profiles[name]
                    affiliate_results = affiliate_profiles[name]

                    results = all_results[idx]
                    classified_official = results.official
                    classified_affiliate = results.affiliate
                    classified_unrelated = results.unrelated

                    marked_official_handles = [x['profile'].handle.lower()
                                               for x in classified_official]
                    marked_affiliate_handles = [x['profile'].handle.lower()
                                                for x in classified_affiliate]
                    marked_unrelated_handles = [x['profile'].handle.lower()
                                                for x in classified_unrelated]
                    official_handles = [x.handle.lower()
                                        for x in official_results]
                    affiliate_handles = [x.handle.lower()
                                         for x in affiliate_results]

                    official_counts = MetricCalculator.count_positives(
                        actual_handles=official_handles,
                        marked_positive_handles=marked_official_handles,
                        marked_negative_handles=(marked_affiliate_handles
                                                 + marked_unrelated_handles))
                    combined_official_results.append(official_counts)

                    affiliate_counts = MetricCalculator.count_positives(
                        actual_handles=affiliate_handles,
                        marked_positive_handles=marked_affiliate_handles,
                        marked_negative_handles=(marked_unrelated_handles
                                                 + marked_official_handles))
                    combined_affiliate_results.append(affiliate_counts)

                official_metrics = MetricCalculator.fold_metrics(
                    combined_official_results)
                affiliate_metrics = MetricCalculator.fold_metrics(
                    combined_affiliate_results)

                result = {
                    'official': official_metrics,
                    'affiliate': affiliate_metrics
                }
                classification_results[classifier_name].append(result)

            fold += 1

        return classification_results

    def evaluate_statistical(self):
        trainer = Trainer(self.profiles, self.profile_type,
                          self.converter, self.network)
        training_set = trainer.generate_training_set()

        profiles = numpy.array(list(self.profiles))
        data = numpy.array(training_set.data)
        labels = numpy.array(training_set.labels)

        fold_iterator = cross_validation.StratifiedKFold(labels,
                                                         n_folds=10,
                                                         shuffle=True,
                                                         random_state=42)

        official_profile_pairs = ((x['name'], self.profile_type(x['profile'],
                                                                x['posts']))
                                  for x in self.profiles if x['label'] == 2)
        affiliate_profile_pairs = ((x['name'], self.profile_type(x['profile'],
                                                                 x['posts']))
                                   for x in self.profiles if x['label'] == 1)

        official_profiles = defaultdict(list)
        for name, profile in official_profile_pairs:
            official_profiles[name].append(profile)

        affiliate_profiles = defaultdict(list)
        for name, profile in affiliate_profile_pairs:
            affiliate_profiles[name].append(profile)

        fold = 1
        # This assumes we're just using Random Forest (i.e. one classifier)
        # Ugly hack for now.
        classification_results = {
            'official_correct': [],
            'affiliate_correct': []
        }
        for train, test in fold_iterator:
            classifiers = initialize_classifiers()

            training_data = data[train]
            training_labels = labels[train]

            test_set = itertools.compress(profiles[test], labels[test])
            company_names = set(x['name'] for x in test_set)
            print 'Test set', fold, '-', len(company_names), 'companies.'

            for classifier in classifiers:
                classifier_name = classifier['type']
                c = classifier['classifier']
                trained = c.fit(training_data, training_labels)

                system = SingleNetworkSearcher(
                    classifier=trained,
                    searchengine=self.search_engine,
                    profile_converter=self.converter,
                    network=self.network)

                number_of_workers = int(multiprocessing.cpu_count() * 0.75)
                worker_pool = ProcessingPool(number_of_workers)
                all_results = worker_pool.map(system.query, company_names)

                for idx, name in enumerate(company_names):
                    official_results = official_profiles[name]
                    affiliate_results = affiliate_profiles[name]

                    results = all_results[idx]
                    classified_official = results.official
                    classified_affiliate = results.affiliate

                    marked_official_handles = [x['profile'].handle.lower()
                                               for x in classified_official]
                    marked_affiliate_handles = [x['profile'].handle.lower()
                                                for x in classified_affiliate]

                    official_handles = [x.handle.lower()
                                        for x in official_results]
                    affiliate_handles = [x.handle.lower()
                                         for x in affiliate_results]

                    official_correct = 0
                    for handle in marked_official_handles:
                        if handle in official_handles:
                            official_correct += 1

                    affiliate_correct = 0
                    for handle in marked_affiliate_handles:
                        if handle in affiliate_handles:
                            affiliate_correct += 1

                    classification_results['official_correct'].append(official_correct)
                    classification_results['affiliate_correct'].append(affiliate_correct)

            fold += 1

        return classification_results


def initialize_classifiers():
    # TODO: should move this into features.py too, so it's specific to a system. Maybe.
    classifiers = [
        # {'type': 'Gaussian Naive Bayes', 'classifier': GaussianNB()},
        # {'type': 'Bernoulli Naive Bayes', 'classifier': BernoulliNB()},
        # {'type': 'Logistic Regression', 'classifier': LogisticRegression()},
        # {'type': 'Multinomial Naive Bayes', 'classifier': MultinomialNB()},
        # {'type': 'Decision Tree', 'classifier': DecisionTreeClassifier()},
        # {'type': 'Support Vector', 'classifier': SVC(probability=True)},
        {'type': 'Random Forest', 'classifier': RandomForestClassifier()}
    ]

    return classifiers


def pretty_print_summary(network_name, results):
    output = [
        network_name
    ]

    official_results = {k: MetricCalculator.overall_metrics([x['official'] for x in v])
                        for k, v in results.iteritems()}
    affiliate_results = {k: MetricCalculator.overall_metrics([x['affiliate'] for x in v])
                         for k, v in results.iteritems()}

    output.extend(generate_metric_outputs(official_results, 'Official'))
    output.extend(generate_metric_outputs(affiliate_results, 'Affiliate'))

    return output


def generate_metric_outputs(scores, class_type):
    classifiers = sorted(scores.keys())

    output = []
    output.append('\n' + class_type)
    output.append('F1 Macro Averages\n')
    for classifier in classifiers:
        line = get_summary_line(scores, classifier, 'macro_average_f1')
        output.append(line)

    output.append('\nP Macro Averages\n')
    for classifier in classifiers:
        line = get_summary_line(scores, classifier, 'macro_average_precision')
        output.append(line)

    output.append('\nR Macro Averages\n')
    for classifier in classifiers:
        line = get_summary_line(scores, classifier, 'macro_average_recall')
        output.append(line)

    output.append('\nF1 Micro Averages\n')
    for classifier in classifiers:
        line = get_summary_line(scores, classifier, 'micro_average_f1')
        output.append(line)

    output.append('\nP Micro Averages\n')
    for classifier in classifiers:
        line = get_summary_line(scores, classifier, 'micro_average_precision')
        output.append(line)

    output.append('\nR Micro Averages\n')
    for classifier in classifiers:
        line = get_summary_line(scores, classifier, 'micro_average_recall')
        output.append(line)

    output.append('\nMax F1\n')
    for classifier in classifiers:
        line = get_summary_line(scores, classifier, 'max_f1')
        output.append(line)

    output.append('\nMax Precision')
    for classifier in classifiers:
        line = get_summary_line(scores, classifier, 'max_precision')
        output.append(line)

    output.append('\nMax Recall')
    for classifier in classifiers:
        line = get_summary_line(scores, classifier, 'max_recall')
        output.append(line)

    return output


def get_summary_line(scores, classifier, key):
    result = scores[classifier][key]
    line = ','.join([classifier, str(result)])
    return line


def calculate_f1(precision, recall):
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2.0 * (precision * recall) / (precision + recall)

    return f1


class MetricCalculator(object):
    """Calculates evaluation metrics for a system's results."""
    @staticmethod
    def count_positives(actual_handles, marked_positive_handles,
                        marked_negative_handles):
        true_positive = 0
        max_true_positive = 0
        for handle in marked_positive_handles:
            if handle in actual_handles:
                true_positive += 1
                max_true_positive += 1

        for handle in marked_negative_handles:
            if handle in actual_handles:
                max_true_positive += 1

        return {
            'true_positive': true_positive,
            'max_true_positive': max_true_positive,
            'marked_positive': len(marked_positive_handles),
            'actual_number_of_positives': len(actual_handles)
        }

    @staticmethod
    def fold_metrics(results):
        """Calculates precision, recall, true positive, false positive,
        false negative, and so on for a particular fold."""

        # The number of positives from our ground truth.
        total_actual_positives = sum(x['actual_number_of_positives']
                                     for x in results)
        # The number of positives that the system returned, whether
        # marked true positive or false negative.
        max_true_positive = sum(x['max_true_positive']
                                for x in results)
        total_marked_positive = sum(x['marked_positive'] for x in results)

        true_positive = sum(x['true_positive'] for x in results)
        false_positive = total_marked_positive - true_positive
        false_negative = total_actual_positives - true_positive

        precision = (0 if total_marked_positive is 0
                     else float(true_positive) / total_marked_positive)
        recall = (float(true_positive)
                  / total_actual_positives)

        return {
            'precision': precision,
            'recall': recall,
            'true_positive': true_positive,
            'false_positive': false_positive,
            'false_negative': false_negative,
            'total_actual_positives': total_actual_positives,
            'max_true_positive': max_true_positive
        }

    @staticmethod
    def overall_metrics(results):
        """Calculates the overall precision, recall, F1, and so on for a
        particular classifier."""
        total_precision = 0.0
        total_recall = 0.0
        total_f1 = 0.0

        total_true_pos = 0.0
        total_false_pos = 0.0
        total_false_neg = 0.0

        total_actual_positives = 0.0
        max_true_positive = 0.0

        for result in results:
            precision = float(result['precision'])
            recall = float(result['recall'])

            total_precision += precision
            total_recall += recall

            if precision + recall == 0:
                f1 = 0.0
            else:
                f1 = 2.0 * (precision * recall) / (precision + recall)
            total_f1 += f1

            total_true_pos += float(result['true_positive'])
            total_false_pos += float(result['false_positive'])
            total_false_neg += float(result['false_negative'])

            total_actual_positives += float(result['total_actual_positives'])
            max_true_positive += float(result['max_true_positive'])

        result_count = len(results)
        macro_average_precision = total_precision / result_count
        macro_average_recall = total_recall / result_count

        macro_average_f1 = calculate_f1(macro_average_precision,
                                        macro_average_recall)

        if total_true_pos + total_false_pos == 0:
            micro_average_precision = 0.0
        else:
            micro_average_precision = total_true_pos / \
                (total_true_pos + total_false_pos)

        if total_true_pos + total_false_neg == 0:
            micro_average_recall = 0.0
        else:
            micro_average_recall = total_true_pos / \
                (total_true_pos + total_false_neg)

        micro_average_f1 = calculate_f1(micro_average_precision,
                                        micro_average_recall)

        max_precision = 1.0
        max_recall = max_true_positive / total_actual_positives
        max_f1 = 2.0 * (max_precision * max_recall) / \
            (max_precision + max_recall)

        return {
            'max_precision': max_precision,
            'max_recall': max_recall,
            'max_f1': max_f1,
            'macro_average_f1': macro_average_f1,
            'macro_average_recall': macro_average_recall,
            'macro_average_precision': macro_average_precision,
            'micro_average_f1': micro_average_f1,
            'micro_average_recall': micro_average_recall,
            'micro_average_precision': micro_average_precision
        }


def evaluate_and_print():
    printer = pretty_print_summary

    twitter_entries = get_twitter_entries()
    twitter_start_time = int(time.time())
    print 'Evaluating Twitter', twitter_start_time
    twitter_evaluator = Evaluator(twitter_entries, TwitterProfile,
                                  TwitterSearch(), 'twitter')
    twitter_results = twitter_evaluator.evaluate()
    twitter_end_time = int(time.time())
    twitter_lines = ['\n' + x for x in printer('Twitter', twitter_results)]

    print 'Done', twitter_end_time, '. Total',\
          twitter_end_time - twitter_start_time

    with open('twitter_evaluation_results.csv', 'w') as twitter_result_file:
        twitter_result_file.writelines(twitter_lines)

    facebook_entries = get_facebook_entries()
    facebook_start_time = int(time.time())
    print 'Evaluating Facebook', facebook_start_time
    facebook_evaluator = Evaluator(facebook_entries, FacebookProfile,
                                   FacebookSearch(), 'facebook')
    facebook_results = facebook_evaluator.evaluate()
    facebook_end_time = int(time.time())
    facebook_lines = ['\n' + x for x in printer('Facebook', facebook_results)]

    print 'Done', facebook_end_time, '. Total',\
          facebook_end_time - facebook_start_time

    with open('facebook_evaluation_results.csv', 'w') as facebook_result_file:
        facebook_result_file.writelines(facebook_lines)

    output_lines = []
    output_lines += twitter_lines
    output_lines += ['\n']
    output_lines += facebook_lines

    with open('evaluation_results.csv', 'w') as result_file:
        result_file.writelines(output_lines)


def process_network_results(results):
    result = SystemEvaluationResult(results)
    return result.process()


def evaluate_to_file(converter=config.evaluate_converter, idx=0):
    name = converter.name
    basedir = os.path.dirname(__file__)
    results_directory = os.path.join(basedir, 'results')

    twitter_entries = get_twitter_entries()
    twitter_start_time = int(time.time())
    print 'Evaluating Twitter', name, twitter_start_time
    twitter_evaluator = Evaluator(twitter_entries, TwitterProfile,
                                  TwitterSearch(), 'twitter',
                                  converter=converter)
    twitter_results = twitter_evaluator.evaluate()
    twitter_end_time = int(time.time())

    processed_results = process_network_results(twitter_results)

    twitter_folder = os.path.join(results_directory, 'Twitter')
    results_file = os.path.join(twitter_folder, '%02d. ' % idx + name)
    cPickle.dump(processed_results, open(results_file, 'wb'))
    print 'Done', twitter_end_time, '. Total',\
          twitter_end_time - twitter_start_time

    facebook_entries = get_facebook_entries()
    facebook_start_time = int(time.time())
    print 'Evaluating Facebook', facebook_start_time
    facebook_evaluator = Evaluator(facebook_entries, FacebookProfile,
                                   FacebookSearch(), 'facebook',
                                   converter=converter)
    facebook_results = facebook_evaluator.evaluate()
    facebook_end_time = int(time.time())

    processed_results = process_network_results(facebook_results)

    facebook_folder = os.path.join(results_directory, 'Facebook')
    results_file = os.path.join(facebook_folder, '%02d. ' % idx + name)
    cPickle.dump(processed_results, open(results_file, 'wb'))
    print 'Done', facebook_end_time, '. Total',\
          facebook_end_time - facebook_start_time


def evaluate_statistical_significance(converter=config.evaluate_converter,
                                      idx=0):
    name = converter.__name__
    basedir = os.path.dirname(__file__)
    results_directory = os.path.join(basedir, 'results')

    twitter_entries = get_twitter_entries()
    twitter_start_time = int(time.time())
    print 'Evaluating Twitter', name, twitter_start_time
    twitter_evaluator = Evaluator(twitter_entries, TwitterProfile,
                                  TwitterSearch(), 'twitter',
                                  converter=converter)
    twitter_results = twitter_evaluator.evaluate_statistical()
    twitter_end_time = int(time.time())

    twitter_folder = os.path.join(results_directory, 'Twitter')
    results_file = os.path.join(twitter_folder, '%02d. ' % idx + name)
    cPickle.dump(twitter_results, open(results_file, 'wb'))
    print 'Done', twitter_end_time, '. Total',\
          twitter_end_time - twitter_start_time

    facebook_entries = get_facebook_entries()
    facebook_start_time = int(time.time())
    print 'Evaluating Facebook', facebook_start_time
    facebook_evaluator = Evaluator(facebook_entries, FacebookProfile,
                                   FacebookSearch(), 'facebook',
                                   converter=converter)
    facebook_results = facebook_evaluator.evaluate_statistical()
    facebook_end_time = int(time.time())

    facebook_folder = os.path.join(results_directory, 'Facebook')
    results_file = os.path.join(facebook_folder, '%02d. ' % idx + name)
    cPickle.dump(facebook_results, open(results_file, 'wb'))
    print 'Done', facebook_end_time, '. Total',\
          facebook_end_time - facebook_start_time


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('type', choices=['config', 'all', 'statistical'])
    args = parser.parse_args()

    if args.type == 'config':
        evaluate_to_file()
    elif args.type == 'all':
        for idx, converter in enumerate(all_converters):
            evaluate_to_file(converter, idx + 1)
    elif args.type == 'statistical':
        for idx, converter in enumerate(all_converters):
            evaluate_statistical_significance(converter, idx + 1)
