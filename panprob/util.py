from collections.abc import Sequence, Iterable
import typing
import itertools


def consecutive_pairs(items: Iterable) -> typing.Iterable[typing.Tuple]:
    """Yield consecutive, non-overlapping pairs of items from an iterable.

    If there are an odd number of items, the last item is omitted.

    Example
    -------
    >>> list(consecutive_pairs([1, 2, 3, 4]))
    [(1, 2), (3, 4)]

    """
    it = iter(items)
    while True:
        try:
            a = next(it)
            b = next(it)
            yield (a, b)
        except StopIteration:
            break


def segment(items: Sequence, predicate: typing.Callable) -> typing.List[typing.List]:
    """Segment a sequence into subsequences based on a predicate.

    The predicate function is used to determine the "break points" of the
    sequence. It should take in a single item from the sequence and return
    True if this item should be the start of a new subsequence; False
    otherwise.

    Example
    -------
    >>> predicate = lambda x: isinstance(x, str)
    >>> segment(["x", 1, 2, "a", 3, "b", 4], predicate)
    [["x", 1, 2], ["a", 3], ["b", 4]]

    Example
    -------
    If the first item in the sequence does not satisfy the predicate, the
    result will be the same as if there was a "break point" at the beginning
    of the sequence:

    >>> predicate = lambda x: isinstance(x, str)
    >>> segment([1, 2, "a", 3, "b", 4], predicate)
    [[1, 2], ["a", 3], ["b", 4]]

    Example
    -------
    If two or more consecutive items satisfy the predicate, they will not be
    grouped together:

    >>> predicate = lambda x: isinstance(x, str)
    >>> segment(["a", 1, 2, 3, "b", "c", 4, 5], predicate)
    [["a", 1, 2, 3], ["b"], ["c", 4, 5]]

    """
    # the idea is simple: insert a sentinel value before each break point, then
    # group by the sentinel value. The groups that don't correspond to sentinels
    # are the segments.

    # place sentinels before each break point
    sentinel = object()

    def items_with_sentinels():
        for item in items:
            if predicate(item):
                yield sentinel
            yield item

    # at this point, our examples look like:
    # ["a", 1, 2, 3, "b", 1, 2, "c", 1, 2, 3, 4]
    #    -> [sentinel, "a", 1, 2, 3, sentinel, "b", 1, 2, sentinel, "c", 1, 2, 3, 4]
    # [1, 2, "a", 3, "b", 4]
    #    -> [1, 2, sentinel, "a", 3, sentinel, "b", 4]
    # and
    # ["a", 1, 2, 3, "b", "c", 4, 5]
    #    -> [sentinel, "a", 1, 2, 3, sentinel, "b", sentinel, "c", 4, 5]

    # recall that itertools.groupby groups consecutive items that have the same
    # key. In our case, the key is whether or not the item is a sentinel, and there
    # will be a sentinel between each segment. So, if we group by the sentinel
    # value, we will get groups that correspond to segments (and groups that correspond
    # to sentinels, but we don't care about those).
    groups = itertools.groupby(items_with_sentinels(), lambda x: x is sentinel)
    return [list(v) for (is_sentinel, v) in groups if not is_sentinel]
