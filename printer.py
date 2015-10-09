import cPickle
import os
import os.path
from collections import defaultdict


def print_all(results_dir):
    """Given the path to the results directory, writes results for each
    network into a CSV file."""
    twitter_directory = os.path.join(results_dir, 'Twitter')
    twitter_results = load_results(twitter_directory)
    processed_twitter_results = process_results_for_printing(twitter_results)

    twitter_lines = ['Twitter']
    twitter_lines += print_network_results(processed_twitter_results)

    facebook_directory = os.path.join(results_dir, 'Facebook')
    facebook_results = load_results(facebook_directory)
    processed_facebook_results = process_results_for_printing(facebook_results)

    facebook_lines = ['\n\nFacebook']
    facebook_lines += print_network_results(processed_facebook_results)

    with open('results.csv', 'w') as results_file:
        results_file.writelines(twitter_lines)
        results_file.writelines(facebook_lines)


def process_results_for_printing(results):
    """Given a dictionary nested in the hierarchy of `system: class: results`,
    returns one nested in a hierarchy of `class: system: results`."""
    # Results are loaded as (system:class:results) nested dictionaries.
    # It's easier to work with them in (class:system:results) form.
    official = {}
    affiliate = {}
    for system, classes in results.iteritems():
        official[system] = classes['official']
        affiliate[system] = classes['affiliate']

    return {
        'official': official,
        'affiliate': affiliate
    }


def print_network_results(results):
    """Given a results dictionary, returns CSV lines for the performance
    of each system, separated by class, then metric (F1, Precision, and
    Recall)."""
    # Split by class, then by metric.
    output_lines = ['\n\nOfficial']
    output_lines += print_class_results(results['official'])
    output_lines += '\n\nAffiliate'
    output_lines += print_class_results(results['affiliate'])

    return output_lines


def print_class_results(results):
    """Given a results dictionary, returns CSV lines for each system's F1,
    precision, and recall."""
    f1 = print_f1(results)
    precision = print_precision(results)
    recall = print_recall(results)

    return f1 + precision + recall


def print_f1(results):
    """Given a results dictionary (nested in `system: results` form), returns
    CSV lines for each system's F1."""
    return print_metric(results, key='f1')


def print_precision(results):
    """Given a results dictionary (nested in `system: results` form), returns
    CSV lines for each system's precision."""
    return print_metric(results, key='precision')


def print_recall(results):
    """Given a results dictionary (nested in `system: results` form), returns
    CSV lines for each system's recall."""
    return print_metric(results, key='recall')


def print_metric(results, key):
    """Given a results dictionary (nested in `system: results` form)
    and a metric (f1, precision, or recall), returns CSV lines for each
    system's results in that metric."""
    output_lines = ['\n\n' + key + ' Averages']

    systems = sorted(results.iterkeys())
    header_line = "," + ",".join(systems)
    output_lines.append('\n' + header_line)

    results_by_classifier = defaultdict(list)

    for system in systems:
        system_results = results[system]

        metrics = system_results[key]
        for classifier, score in metrics.iteritems():
            results_by_classifier[classifier].append(str(score))

    for classifier, results in sorted(results_by_classifier.iteritems(),
                                      key=lambda x: x[0]):
        classifier_line = ",".join([classifier] + results)
        output_lines.append('\n' + classifier_line)

    return output_lines


def load_results(directory):
    """Loads all result dictionaries in the given directory,
    and returns them in a dictionary keyed by their system's name."""
    results = {}
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        results[filename] = cPickle.load(open(path, 'rb'))

    return results

if __name__ == '__main__':
    this_directory = os.path.dirname(__file__)
    results_dir = os.path.join(this_directory, 'results')

    print_all(results_dir)
