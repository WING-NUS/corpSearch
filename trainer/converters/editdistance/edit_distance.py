import string

from nltk.metrics import edit_distance

from stopwords import Stopwords


# TODO: add tests for every method here.
class EditDistanceStopwords(object):
    @staticmethod
    def edit_distance(first, second):
        """Returns the edit distance between two strings, with
        stopwords stripped. The list of stopwords can be found in the Stopwords
        class.

        >>> EditDistanceStopwords.edit_distance("abc", "abc")
        0

        >>> EditDistanceStopwords.edit_distance("abc", "def")
        3

        >>> EditDistanceStopwords.edit_distance("Boeing Corporation", "Boeing")
        0
        """
        first_processed = strip_stopwords(first)
        second_processed = strip_stopwords(second)

        return EditDistance.edit_distance(first_processed,
                                          second_processed)

    @staticmethod
    def without_spaces(first, second):
        """Returns the normalized edit distance between two strings, with
        spaces and stopwords stripped out.

        >>> EditDistanceStopwords.without_spaces("BoeingCorporation", "Boeing")
        0
        """
        first_processed = strip_stopwords(first)
        second_processed = strip_stopwords(second)

        return EditDistance.without_spaces(first_processed,
                                           second_processed)

    @staticmethod
    def with_abbreviations(to_abbreviate, abbreviated):
        """Returns the edit distance between two strings, with
        simple abbreviations handled after stopwords have been stripped.

        >>> EditDistanceStopwords.with_abbreviations(to_abbreviate="Hewlett Packard Company", abbreviated="HP")
        0
        """
        first_processed = strip_stopwords(to_abbreviate)
        second_processed = strip_stopwords(abbreviated)

        return EditDistance.with_abbreviations(first_processed,
                                               second_processed)


class NormalizedEditDistanceStopwords(object):

    @staticmethod
    def edit_distance(first, second):
        """Returns the normalized edit distance between two strings, with
        stopwords stripped. The list of stopwords can be found in the Stopwords
        class.

        >>> NormalizedEditDistanceStopwords.edit_distance("abc", "abc")
        1.0

        >>> NormalizedEditDistanceStopwords.edit_distance("abc", "def")
        0.0

        >>> NormalizedEditDistanceStopwords.edit_distance("Boeing Corporation", "Boeing")
        1.0
        """
        first_processed = strip_stopwords(first)
        second_processed = strip_stopwords(second)

        return NormalizedEditDistance.edit_distance(first_processed,
                                                    second_processed)

    @staticmethod
    def without_spaces(first, second):
        """Returns the normalized edit distance between two strings, with
        spaces and stopwords stripped out.

        >>> NormalizedEditDistanceStopwords.without_spaces("BoeingCorporation", "Boeing")
        1.0
        """
        first_processed = strip_stopwords(first)
        second_processed = strip_stopwords(second)

        return NormalizedEditDistance.without_spaces(first_processed,
                                                     second_processed)

    @staticmethod
    def with_abbreviations(to_abbreviate, abbreviated):
        """Returns the normalized edit distance between two strings, with
        simple abbreviations handled after stopwords have been stripped.

        >>> NormalizedEditDistanceStopwords.with_abbreviations(to_abbreviate="Hewlett Packard Company", abbreviated="HP")
        1.0
        """
        first_processed = strip_stopwords(to_abbreviate)
        second_processed = strip_stopwords(abbreviated)

        return NormalizedEditDistance.with_abbreviations(first_processed,
                                                         second_processed)


class NormalizedEditDistance(object):

    @staticmethod
    def edit_distance(first, second):
        """Returns the normalized edit distance between two strings.

        Normalized edit distance ranges between 0 and 1, where 0 indicates the
        maximum number of changes are made - max(len(first, second) - and 1
        indicates no changes are necessary.

        >>> NormalizedEditDistance.edit_distance("abc", "abc")
        1.0
        >>> NormalizedEditDistance.edit_distance("abc", "def")
        0.0
        >>> NormalizedEditDistance.edit_distance("abcd", "abef")
        0.5
        """
        distance = float(edit_distance(first, second))

        max_distance = max([len(first), len(second)])

        if max_distance == 0:
            # Both strings are empty.
            return 0

        return 1 - distance / max_distance

    @staticmethod
    def without_spaces(first, second):
        first_processed = strip_spaces_and_punctuation(first)
        second_processed = strip_spaces_and_punctuation(second)

        return NormalizedEditDistance.edit_distance(first_processed,
                                                    second_processed)

    @staticmethod
    def with_abbreviations(to_abbreviate, abbreviated):
        """
        Returns the normalized edit distance between two strings, with simple
        abbreviations taken into account. This assumes one of the two strings
        is already abbreviated, as in the following example:

        >>> NormalizedEditDistance.with_abbreviations("Hewlett Packard", "HP")
        1.0

        To ensure correctness, named parameters should be used:
        >>> NormalizedEditDistance.with_abbreviations(abbreviated="HP", to_abbreviate="Hewlett Packard")
        1.0

        >>> NormalizedEditDistance.with_abbreviations("Dell", "Dell")
        1.0
        >>> NormalizedEditDistance.with_abbreviations("abc", "abc")
        1.0
        >>> NormalizedEditDistance.with_abbreviations("abc", "def")
        0.0
        >>> NormalizedEditDistance.with_abbreviations("abcd", "abef")
        0.5
        """
        abbreviation = abbreviate(to_abbreviate)

        abbreviation_score = NormalizedEditDistance.edit_distance(abbreviation,
                                                                  abbreviated)
        regular_score = NormalizedEditDistance.without_spaces(to_abbreviate,
                                                              abbreviated)

        return max(abbreviation_score, regular_score)


class EditDistance(object):

    @staticmethod
    def edit_distance(first, second):
        return edit_distance(first, second)

    @staticmethod
    def without_spaces(first, second):
        first_processed = strip_spaces_and_punctuation(first)
        second_processed = strip_spaces_and_punctuation(second)

        return EditDistance.edit_distance(first_processed, second_processed)

    @staticmethod
    def with_abbreviations(to_abbreviate, abbreviated):
        abbreviation = abbreviate(to_abbreviate)

        abbreviation_score = EditDistance.edit_distance(abbreviation,
                                                        abbreviated)
        regular_score = EditDistance.without_spaces(to_abbreviate, abbreviated)

        return min(abbreviation_score, regular_score)


def strip_spaces_and_punctuation(text):
    minus_punctuation = strip_punctuation(text)
    minus_punctuation_and_spaces = "".join(minus_punctuation.split())
    minus_punctuation_and_spaces = "".join(minus_punctuation.split())

    return minus_punctuation_and_spaces


def strip_punctuation(text):
    return reduce(lambda s,
                  char: s.replace(char, ''),
                  string.punctuation,
                  text)


def strip_stopwords(text):
    processed = strip_punctuation(text)
    for stopword in Stopwords.words:
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
    no_punctuation = strip_punctuation(text).split()
    first_letters = [i[0] for i in no_punctuation]
    abbreviation = "".join(first_letters).strip()

    return abbreviation
