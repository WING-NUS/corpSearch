
class BaseTokenizer(object):
    """The simplest tokenizer: splits strings by whitespace."""
    @staticmethod
    def tokenize(string):
        return string.split()


class LowerTokenizer(object):
    """Casts strings to lower-case before splitting by whitespace."""
    @staticmethod
    def tokenize(string):
        lowered = string.lower()
        return BaseTokenizer.tokenize(lowered)
