import pytest

from bwt_compressor.segment_tree import SegmentTree


def test_get_sum():
    leafs = [1,3,5,7,9,11]
    n = len(leafs)
    segment_tree = SegmentTree(leafs)
    assert segment_tree.get_sum(0, n) == sum(leafs)
    assert segment_tree.get_sum(0, n-1) == sum(leafs[:-1])
    assert segment_tree.get_sum(1, n-1) == sum(leafs[1:-1])
    assert segment_tree.get_sum(4, n-3) == sum(leafs[4:-3])


def test_update():
    leafs = [1,3,5,7,9,11]
    n = len(leafs)
    diff = 2
    segment_tree = SegmentTree(leafs)
    segment_tree.update(1, diff)
    assert segment_tree.get_sum(1, 2) == leafs[1] + diff
    assert segment_tree.get_sum(0, n) == sum(leafs) + diff
    assert segment_tree.get_sum(2, n) == sum(leafs[2:])
