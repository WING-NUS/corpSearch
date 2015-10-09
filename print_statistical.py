import cPickle
import os


def print_all(results_dir):
    """Given the path to the results directory, creates .csv files containing
    the data needed to calculate statistical significance for feature sets
    on each network."""
    twitter_directory = os.path.join(results_dir, 'Twitter')
    twitter_results = load_results(twitter_directory)

    print_network_results('Twitter', twitter_results)

    facebook_directory = os.path.join(results_dir, 'Facebook')
    facebook_results = load_results(facebook_directory)

    print_network_results('Facebook', facebook_results)


def print_network_results(network, results):
    """Given the name of the social network and its corresponding result
    dictionary, outputs results for that network to a .csv file."""
    header_row = ['Query'] + sorted(results.keys())
    with open(network + '-official.csv', 'w') as official_file:
        official_file.write(','.join(header_row) + '\n')

        systems = sorted(results.keys())
        number_of_queries = len(results[systems[0]]['official_correct'])

        for index in range(number_of_queries):
            line = [index]
            for system in systems:
                line.append(results[system]['official_correct'][index])

            official_file.write(','.join(str(x) for x in line) + '\n')

    with open(network + '-affiliate.csv', 'w') as affiliate_file:
        affiliate_file.write(','.join(header_row) + '\n')

        systems = sorted(results.keys())
        number_of_queries = len(results[systems[0]]['affiliate_correct'])

        for index in range(number_of_queries):
            line = [index]
            for system in systems:
                line.append(results[system]['affiliate_correct'][index])

            affiliate_file.write(','.join(str(x) for x in line) + '\n')


def load_results(directory):
    """Loads all result dictionaries in the given directory,
    and returns them in a dictionary keyed by the system name."""
    results = {}
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        results[filename] = cPickle.load(open(path, 'rb'))

    return results

if __name__ == '__main__':
    this_directory = os.path.dirname(__file__)
    results_dir = os.path.join(this_directory, 'results')
    print_all(results_dir)
