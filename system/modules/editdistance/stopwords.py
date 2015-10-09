import string

from .. import BaseFeature
from distance import NormalizedEditDistance

# Since we remove by substring, this list must be sorted such that
# longer forms are taken out first. (e.g. if "Co" is before "Corp",
# we end up with "rp" being left.)
words = [
    "Companies",
    "Company",
    "Corporation",
    "Corp",
    "Co",
    "Cos",
    "Group",
    "Incorporated",
    "Inc",
    "Limited",
    "Ltd",
    "LLLP",
    "LP",
    "The",
    "Holding",
    "and"
]


def strip_spaces_and_punctuation(text):
    """Strips spaces and punctuation from a given string."""
    minus_punctuation = strip_punctuation(text)
    minus_punctuation_and_spaces = "".join(minus_punctuation.split())
    minus_punctuation_and_spaces = "".join(minus_punctuation.split())

    return minus_punctuation_and_spaces


def strip_punctuation(text):
    """Strips punctuation from a given string."""
    return reduce(lambda s,
                  char: s.replace(char, ''),
                  string.punctuation,
                  text)


def strip_stopwords(text):
    """Strips common stopwords from a given string. These are words
    which frequently appear in company names."""
    processed = strip_punctuation(text)
    for stopword in words:
        # We want to compare lower-case, but return the original casing.
        lowered = processed.lower()
        stopword_lowered = stopword.lower()

        # There may be more than one occurrence of the stopword.
        # This prevents cases like "Robco Co." from being handled incorrectly.
        while stopword_lowered in lowered:
            stopword_length = len(stopword)
            index = lowered.find(stopword_lowered)

            processed = processed[:index] + processed[index+stopword_length:]
            lowered = processed.lower()

    return processed.strip()


def abbreviate(text):
    """Returns a simple abbreviation for a string, consisting of the first
    characters of each word."""
    no_punctuation = strip_punctuation(text).split()
    first_letters = [i[0] for i in no_punctuation]
    abbreviation = "".join(first_letters).strip()

    return abbreviation


class NormalizedEditDistanceStopwords(object):
    @staticmethod
    def between(a, b):
        """Returns the normalized edit distance between two strings.

        This also strips out stopwords and punctuation from either string,
        and returns the maximum score with or without them.

        >>> NormalizedEditDistanceStopwords.between("abc", "abc")
        1.0
        >>> NormalizedEditDistanceStopwords.between("Boeing Corporation, "Boeing")
        1.0
        >>> NormalizedEditDistanceStopwords.between("abcd", "abef")
        0.5
        """

        a_processed = strip_stopwords(a)
        b_processed = strip_stopwords(b)

        return max(NormalizedEditDistance.between(a, b_processed),
                   NormalizedEditDistance.between(a_processed, b),
                   NormalizedEditDistance.between(a, b),
                   NormalizedEditDistance.between(a_processed, b_processed))


class NormalizedEditDistanceStopwordsQueryToHandle(BaseFeature):
    """The normalized edit distance between the query and the handle, with
    stopwords removed from both."""
    @staticmethod
    def feature_labels():
        return [
            'Normalized Edit Distance (Stopwords, Abbreviations): Query to Handle'
        ]

    @staticmethod
    def score(query, profile, data=None):
        return [
            NormalizedEditDistanceStopwords.between(query, profile.handle)
        ]


class NormalizedEditDistanceStopwordsQueryToDisplayName(BaseFeature):
    """The normalized edit distance between the query and the display name,
    with stopwords removed from both."""
    @staticmethod
    def feature_labels():
        return [
            'Normalized Edit Distance (Stopwords, Abbreviations): Query to Display Name'
        ]

    @staticmethod
    def score(query, profile, data=None):
        return [
            NormalizedEditDistanceStopwords.between(query, profile.display_name)
        ]
