from collections import Counter
import math

START_SYMBOL = "START"
END_SYMBOL = "END"
MINIMUM_THRESHOLD = 2


def bigrams(text):
    """Given an input string, returns a list of all bigrams found within.

    >>> bigrams("The quick brown fox.")
    [('START', 'The'), ('The', 'quick'), ('quick', 'brown'), ('brown', 'fox.'), ('fox.', 'END')]

    >>> bigrams("Test")
    [('START', 'Test'), ('Test', 'END')]
    """
    tokens = text.split()
    tokens.insert(0, START_SYMBOL)
    tokens.append(END_SYMBOL)

    return zip(tokens, tokens[1:])


def bigram_counts(text):
    """Given an input string, returns a dictionary keyed by bigram, with values
    corresponding to the amount of times that bigram appears.
    """

    bigram_list = bigrams(text)
    return Counter(bigram_list)


class BigramLanguageModel(object):
    """Represents a bigram language model for some collection of text."""
    def __init__(self):
        self.counts = Counter()

    def add(self, text):
        """Adds the given string to the language model."""
        grams = bigrams(text)
        self.counts.update(grams)

    def prune(self):
        """Removes bigrams that appear less than MINIMUM_THRESHOLD times."""
        infrequent_bigrams = (x[0] for x in self.counts.items()
                              if x[1] < MINIMUM_THRESHOLD)
        for bigram in infrequent_bigrams:
            del self.counts[bigram]

    def probability(self, text):
        """Gives the base-10 log probability that the given text appears in
        this model."""
        text_bigrams = bigrams(text)

        total_counts = sum(self.counts.itervalues())
        number_of_items = len(self.counts)

        new_tokens = set(x for x in text_bigrams if self.counts[x] == 0)
        smoothed_total = total_counts + number_of_items + len(new_tokens)

        probability = 0.0
        for bigram in text_bigrams:
            count = self.counts[bigram] + 1.0
            this_probability = -math.log(count / smoothed_total, 10)

            probability += this_probability

        return probability
