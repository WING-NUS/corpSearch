from ..vectorspace import VectorSpaceSearch


def test_identical_query():
    documents = [
        'The quick brown fox',
    ]
    vs = VectorSpaceSearch(documents)

    query = 'The quick brown fox'

    expected = [(0, 1.0)]
    assert expected == vs.query(query)
