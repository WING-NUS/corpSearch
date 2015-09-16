from ..tokenizers import *


class TestTokenizers:
    def test_base_string_properly_split(self):
        sentence = "The quick brown fox jumped over the lazy dog."
        expected = ["The", "quick", "brown", "fox", "jumped", "over", "the",
                    "lazy", "dog."]

        assert BaseTokenizer.tokenize(sentence) == expected

    def test_string_properly_lowered(self):
        sentence = "The Quick Brown Fox Jumped Over The Lazy Dog."
        expected = ["the", "quick", "brown", "fox", "jumped", "over", "the",
                    "lazy", "dog."]

        assert LowerTokenizer.tokenize(sentence) == expected
