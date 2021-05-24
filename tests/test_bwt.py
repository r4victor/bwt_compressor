import random
import string

import pytest

from bwt_compressor.bwt import (
    _build_suffix_array,
    _compute_sorting_permutation,
    _compute_sorting_permutation_inverse,
    apply_bwt,
    restore_text_from_bwt
)

@pytest.mark.parametrize(
    ['text', 'expected_bwt'],
    [
        ('', '\x00'),
        ('a', 'a\x00'),
        ('aaaaaa', 'aaaaaa\x00'),
        ('banana', 'annb\x00aa'),
    ]
)
def test_apply_bwt(text, expected_bwt):
    assert apply_bwt(text) == expected_bwt


@pytest.mark.parametrize(
    ['text', 'expected_suffix_array'],
    [
        ('', []),
        ('a', [0]),
        ('aaaaaa', [5,4,3,2,1,0]),
        ('banana', [3,2,5,1,4,0]),
    ]
)
def test_build_suffix_array(text, expected_suffix_array):
    assert _build_suffix_array(text) == expected_suffix_array


def test_apply_restore_bwt(max_len=100):
    random.seed(17)
    for l in range(max_len):
        text = ''.join(random.choice(string.ascii_letters) for _ in range(l))
        bwt = apply_bwt(text)
        text_from_bwt = restore_text_from_bwt(bwt)
        assert text_from_bwt == text


@pytest.mark.parametrize(
    ['text', 'expected_sorting_permutation_inverse'],
    [
        ('', []),
        ('a', [0]),
        ('ababc', [0, 2, 1, 3, 4]),
    ]
)
def test_compute_sorting_permutation_inverse(text, expected_sorting_permutation_inverse):
    assert (
        _compute_sorting_permutation(text) ==
        expected_sorting_permutation_inverse
    )


def test_compute_sorting_permutation_inverse_random(max_len=20):
    random.seed(17)
    for l in range(max_len):
        text = ''.join(random.choice(string.ascii_letters) for _ in range(l))
        sorting_permutation_inverse = _compute_sorting_permutation_inverse(text)
        permuted_sorted_text = [None] * len(text)
        for c, pos in zip(sorted(text), sorting_permutation_inverse):
            permuted_sorted_text[pos] = c
        assert ''.join(permuted_sorted_text) == text


@pytest.mark.parametrize(
    ['text', 'expected_sorting_permutation'],
    [
        ('', []),
        ('a', [0]),
        ('ababc', [0, 2, 1, 3, 4]),
    ]
)
def test_compute_sorting_permutation(text, expected_sorting_permutation):
    assert (
        _compute_sorting_permutation(text) ==
        expected_sorting_permutation
    )