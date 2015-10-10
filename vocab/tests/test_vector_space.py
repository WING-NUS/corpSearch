from ..vectorspace import VectorSpaceSearch


def test_identical_query():
    """Tests that a query that is identical to a document returns a
    cosine similarity of 1.0."""
    documents = [
        'The quick brown fox',
    ]
    vs = VectorSpaceSearch(documents)

    query = 'The quick brown fox'

    expected = [(0, 1.0)]
    assert expected == vs.query(query)
