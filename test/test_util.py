from panprob import util

# consecutive_pairs ====================================================================


def test_consecutive_pairs_on_simple_example():
    lst = [1, 2, 3, 4]

    pairs = util.consecutive_pairs(lst)

    assert list(pairs) == [(1, 2), (3, 4)]


def test_consecutive_pairs_omits_last_item_if_odd_number_of_items():
    lst = [1, 2, 3, 4, 5]

    pairs = util.consecutive_pairs(lst)

    assert list(pairs) == [(1, 2), (3, 4)]


# segment ==============================================================================


def test_segment_on_simple_example():
    lst = ["a", 1, 2, 3, "b", 1, 2, "c", 1, 2, 3, 4]

    predicate = lambda x: isinstance(x, str)

    segments = util.segment(lst, predicate)

    assert segments == [
        ["a", 1, 2, 3],
        ["b", 1, 2],
        ["c", 1, 2, 3, 4],
    ]

def test_segment_with_consecutive_break_points():
    lst = ["a", 1, 2, 3, "b", "c", 4, 5]
    predicate = lambda x: isinstance(x, str)
    segments = util.segment(lst, predicate)
    assert segments == [["a", 1, 2, 3], ["b"], ["c", 4, 5]]


def test_segment_when_predicate_is_false_for_first_item():
    """Should segment the list as if there was a break point at the beginning."""
    lst = [1, 2, 3, "b", 1, 2, "c", 1, 2, 3, 4]

    predicate = lambda x: isinstance(x, str)

    segments = util.segment(lst, predicate)

    assert segments == [
        [1, 2, 3],
        ["b", 1, 2],
        ["c", 1, 2, 3, 4],
    ]


def test_segment_when_predicate_is_true_for_last_item():
    lst = ["a", 1, 2, 3, "b", 1, 2, "c", 1, 2, "x"]
    predicate = lambda x: isinstance(x, str)
    segments = util.segment(lst, predicate)
    assert segments == [["a", 1, 2, 3], ["b", 1, 2], ["c", 1, 2], ["x"]]
