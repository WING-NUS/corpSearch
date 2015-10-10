from ..tokenizers import *


class TestTokenizers:
    def test_base_string_properly_split(self):
        """Tests that the BaseTokenizer correctly tokenizes a string by
        whitespace."""
        sentence = "The quick brown fox jumped over the lazy dog."
        expected = ["The", "quick", "brown", "fox", "jumped", "over", "the",
                    "lazy", "dog."]

        assert BaseTokenizer.tokenize(sentence) == expected

    def test_string_properly_lowered(self):
        """Tests that the LowerTokenizer correctly converts a string
        to lower-case before tokenizing."""
        sentence = "The Quick Brown Fox Jumped Over The Lazy Dog."
        expected = ["the", "quick", "brown", "fox", "jumped", "over", "the",
                    "lazy", "dog."]

        assert LowerTokenizer.tokenize(sentence) == expected
