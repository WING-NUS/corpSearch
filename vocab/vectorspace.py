from gensim import corpora, models
from gensim.matutils import cossim
import config


class VectorSpace(object):
    """Represents the vector space for a particular corpus."""
    def __init__(self, tokenized_documents):
        self.dictionary = corpora.Dictionary(tokenized_documents)

    def vector_for_document(self, tokenized_document, update=False):
        """Returns a vector for the given tokenized document (list of strings).
        Uses the bag-of-words model.

        If update is True, also adds any new words in the document to the
        corpora. Otherwise, unknown words are ignored."""
        return self.dictionary.doc2bow(document=tokenized_document,
                                       allow_update=update)


class VectorSpaceSearch(object):
    """Represents a VSM-based search for a given corpus. Returns results
    sorted by cosine-similarity between a query and the stored documents in
    the corpus."""
    def __init__(self, documents):
        self.tokenizer = config.tokenizer

        tokenized = (self.tokenizer.tokenize(document) for document in documents)
        self.vectorspace = VectorSpace(tokenized)
        self.documents = documents

    def query(self, query, sorted=False):
        """Given a search query, returns a list of document IDs and their
        cosine similarity to that query.

        If sorted is True, results are returned sorted in descending order of
        cosine similarity. Otherwise, results are returned ordered by document
        ID."""
        tokenized = self.tokenizer.tokenize(query)
        query_vector = self.vectorspace.vector_for_document(tokenized,
                                                            update=True)

        results = []
        for index, document in enumerate(self.documents):
            tokenized = self.tokenizer.tokenize(document)
            document_vector = self.vectorspace.vector_for_document(tokenized)
            similarity = cossim(query_vector, document_vector)
            results.append((index, similarity))

        if sorted:
            return sorted(results, key=lambda item: -item[1])

        return results
