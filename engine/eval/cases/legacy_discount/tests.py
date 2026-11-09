from solution import calc


def test_gold_bulk():
    assert calc(10, "gold", 11) == 88.0


def test_gold_small():
    assert calc(10, "gold", 5) == 45.0


def test_silver_bulk():
    assert calc(10, "silver", 11) == 99.0


def test_silver_small():
    assert calc(10, "silver", 2) == 19.0


def test_no_tier():
    assert calc(10, "none", 3) == 30.0
