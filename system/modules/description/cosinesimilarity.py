from gensim.matutils import cossim

from .. import BaseFeature
from vocab.vectorspace import VectorSpace
from vocab.tokenizers import LowerTokenizer
from duckduckdescription import DuckDuckDescription


class CosineSimilarityDescriptionAndQuery(BaseFeature):
    """Cosine similarity between the profile description and the query."""
    @staticmethod
    def feature_labels():
        return ['Cosine Similarity: Profile Description and Query']

    @staticmethod
    def score(query, profile, data=None):
        if not len(profile.description):
            return [-1]

        vectorspace = VectorSpace([])

        tokenized_query = LowerTokenizer.tokenize(query)
        tokenized_description = LowerTokenizer.tokenize(profile.description)

        query_vector = vectorspace.vector_for_document(
            tokenized_document=tokenized_query,
            update=True)

        description_vector = vectorspace.vector_for_document(
            tokenized_document=tokenized_description,
            update=True)

        return [cossim(description_vector, query_vector)]


class CosineSimilarityDescriptionAndDDG(BaseFeature):
    """Cosine similarity between the profile description and a description
    retrieved from the DuckDuckGo search engine."""
    @staticmethod
    def feature_labels():
        return ['Cosine Similarity: Profile Description and DDG Description']

    @staticmethod
    def score(query, profile, data=None):
        if not len(profile.description):
            return [-1]

        vectorspace = VectorSpace([])

        tokenized_description = LowerTokenizer.tokenize(profile.description)
        description_vector = vectorspace.vector_for_document(
            tokenized_document=tokenized_description,
            update=True)

        ddg_description = DuckDuckDescription.query(query.lower())

        ddg_vector = []
        if ddg_description:
            ddg_text = ddg_description['description']['text']
            ddg_tokenized = LowerTokenizer.tokenize(ddg_text)
            ddg_vector = vectorspace.vector_for_document(
                tokenized_document=ddg_tokenized,
                update=True)

        if not len(ddg_vector):
            return [-1]

        return [cossim(description_vector, ddg_vector)]
