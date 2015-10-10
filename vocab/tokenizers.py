
class BaseTokenizer(object):
    """The simplest tokenizer: splits strings by whitespace."""
    @staticmethod
    def tokenize(string):
        """Tokenizes the given string.

        >>> BaseTokenizer.tokenize('Hello world.')
        ['Hello', 'world.']
        """
        return string.split()


class LowerTokenizer(object):
    """Casts strings to lower-case before splitting by whitespace."""
    @staticmethod
    def tokenize(string):
        """Tokenizes the given string.

        >>> LowerTokenizer.tokenize('Hello world.')
        ['hello', 'world.']
        """
        lowered = string.lower()
        return BaseTokenizer.tokenize(lowered)
