import itertools
import warnings

from pydivsufsort import divsufsort

from bwt_compressor.common import (
    ALPHABET_SIZE,
    TERMINATOR_SYMBOL
)


def apply_bwt(text):
    assert TERMINATOR_SYMBOL not in text

    suffix_array = _build_suffix_array(text)

    bwt = [None] * len(text)
    for suffix_start_index, sorted_position in enumerate(suffix_array):
        if suffix_start_index != 0:
            bwt[sorted_position] = text[suffix_start_index - 1]
        else:
            bwt[sorted_position] = TERMINATOR_SYMBOL

    first_char = text[-1] if len(text) > 0 else TERMINATOR_SYMBOL

    return first_char + ''.join(bwt)


def _build_suffix_array(text):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        sorted_ranks = divsufsort(text)
    return _compute_inverse_permutation(sorted_ranks)


def _build_suffix_array_naive(text):
    """
    Construct the suffix array in O(n^2logn).
    """
    sorted_ranks = [i for _, i in sorted((text[i:], i) for i in range(len(text)))]
    return _compute_inverse_permutation(sorted_ranks)


def restore_text_from_bwt(bwt):
    sorting_permutation_inverse = _compute_sorting_permutation_inverse(bwt)
    text = [None] * (len(bwt) - 1)
    cur_pos = bwt.find(TERMINATOR_SYMBOL)
    for i in range(len(text)):
        cur_pos = sorting_permutation_inverse[cur_pos]
        text[i] = bwt[cur_pos]
    return ''.join(text)


def _compute_sorting_permutation_inverse(text):
    sorting_permutation = _compute_sorting_permutation(text)
    return _compute_inverse_permutation(sorting_permutation)


def _compute_sorting_permutation(text):
    counters = _get_chars_counters(text)
    start_positions = _get_chars_start_positions(counters)
    sorting_permutation = [None] * len(text)
    for i, c in enumerate(text):
        sorting_permutation[i] = start_positions[ord(c)]
        start_positions[ord(c)] += 1
    return sorting_permutation


def _get_chars_counters(text):
    counters = [0] * ALPHABET_SIZE
    for c in text:
        counters[ord(c)] += 1
    return counters


def _get_chars_start_positions(counters):
    return list(itertools.accumulate([0] + counters))[:-1]


def _compute_inverse_permutation(permutation):
    inverse_permutation = [None] * len(permutation)
    for i, j in enumerate(permutation):
        inverse_permutation[j] = i
    return inverse_permutation