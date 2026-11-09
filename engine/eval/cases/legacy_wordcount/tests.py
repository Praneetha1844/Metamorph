from solution import wc


def test_counts_repeated_words():
    assert wc("a b a") == {"a": 2, "b": 1}


def test_ignores_case_and_edge_punctuation():
    assert wc("Hello, hello!") == {"hello": 2}


def test_empty_and_punctuation_only():
    assert wc("") == {}
    assert wc("...") == {}
