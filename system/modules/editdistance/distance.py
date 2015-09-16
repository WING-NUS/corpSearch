from nltk.metrics import edit_distance


class EditDistance(object):

    @staticmethod
    def between(a, b):
        """Returns the edit distance between two strings.

        >>> EditDistance.between('abc', 'abc')
        0
        >>> EditDistance.between('abc', 'def')
        3
        >>> EditDistance.between('abcd', 'abef')
        2
        """
        return edit_distance(a, b)


class NormalizedEditDistance(object):

    @staticmethod
    def between(a, b):
        """Returns the normalized edit distance between two strings.

        Normalized edit distance ranges between 0 and 1, where 0 indicates the
        maximum number of changes are made - max(len(first, second) - and 1
        indicates no changes are necessary.

        >>> NormalizedEditDistance.between("abc", "abc")
        1.0
        >>> NormalizedEditDistance.between("abc", "def")
        0.0
        >>> NormalizedEditDistance.between("abcd", "abef")
        0.5
        """
        distance = edit_distance(a, b)
        max_distance = float(max([len(a), len(b)]))

        if max_distance == 0:
            # Both strings are empty.
            return 0

        return 1 - distance / max_distance
