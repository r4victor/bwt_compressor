import random
import string

import pytest


from bwt_compressor.common import (
    ALPHABET_SIZE
)

from bwt_compressor.dc import (
    _compute_char_distances,
    _get_alphabet,
    _reduce_char_distances,
    dc_decode,
    dc_encode
)


@pytest.mark.parametrize(
    ['text', 'expected_char_distances'],
    [
        ('', []),
        ('aa', [1,0]),
        ('AZ\x00', [0,0,0]),
        ('abbbdacced', [5,1,1,0,5,0,1,0,0,0]),
    ]
)
def test_compute_char_distances(text, expected_char_distances):
    text = _get_alphabet() + text
    alphabet_char_distances = [0] * ALPHABET_SIZE
    for i, c in enumerate(text[ALPHABET_SIZE:]):
        if alphabet_char_distances[ord(c)] == 0:
            alphabet_char_distances[ord(c)] = ALPHABET_SIZE - ord(c) + i
    assert (
        _compute_char_distances(text) ==
        alphabet_char_distances + expected_char_distances
    )


@pytest.mark.parametrize(
    ['text', 'expected_reduced_char_distances'],
    [
        ('', []),
        ('ab', [0,0]),
        ('abaab', [1,2,1,0,0]),
    ]
)
def test_reduce_char_distances(text, expected_reduced_char_distances):
    text = _get_alphabet() + text
    char_distances = _compute_char_distances(text)
    reduced_char_distances = _reduce_char_distances(text, char_distances)
    assert (
        _reduce_char_distances(text, char_distances)[ALPHABET_SIZE:] ==
        expected_reduced_char_distances
    )


def test_reduce_char_distances_with_alphabet():
    text = 'AZ\x00'
    alphabet = _get_alphabet()
    alphabet_char_distances = [0] * len(alphabet)
    alphabet_char_distances[0] = len(alphabet) + len(text) - 1
    alphabet_char_distances[ord('A')] = 191
    alphabet_char_distances[ord('Z')] = 167
    expected_reduced_alphabet_char_distances = [0] * len(alphabet)
    expected_reduced_alphabet_char_distances[0] = len(text)
    expected_reduced_alphabet_char_distances[ord('A')] = 1
    expected_reduced_alphabet_char_distances[ord('Z')] = 1
    assert (
        _reduce_char_distances(alphabet + text, alphabet_char_distances + [0,0,0]) ==
        expected_reduced_alphabet_char_distances + [0,0,0]
    )


def test_dc_encode():
    text = 'AZ\x00'
    alphabet_expected_dc = [0] * ALPHABET_SIZE
    alphabet_expected_dc[0] = len(text)
    alphabet_expected_dc[ord('A')] = 1
    alphabet_expected_dc[ord('Z')] = 1
    assert dc_encode(text) == [len(text)] + alphabet_expected_dc + [0, 0, 0]


def test_dc_decode_empty():
    dc = [0] * (ALPHABET_SIZE + 1)
    assert dc_decode(dc) == ''


def test_dc_decode_single_letter():
    alphabet_dc = [0] * ALPHABET_SIZE
    alphabet_dc[ord('a')] = 1
    dc = [1] + alphabet_dc + [0]
    assert dc_decode(dc) == 'a'


def test_dc_decode_consecutive():
    text = 'aaaaa'
    alphabet_dc = [0] * ALPHABET_SIZE
    alphabet_dc[ord('a')] = 1
    dc = [len(text)] + alphabet_dc + [0]
    assert dc_decode(dc) == text


def test_dc_decode_nullbyte():
    text = 'AZ\x00'
    alphabet_dc = [0] * ALPHABET_SIZE
    alphabet_dc[0] = len(text)
    alphabet_dc[ord('A')] = 1
    alphabet_dc[ord('Z')] = 1
    dc = [len(text)] + alphabet_dc + [0, 0, 0]
    assert dc_decode(dc) == text


def test_dc_encode_decode(max_len=100):
    random.seed(20)
    for l in range(max_len):
        text = ''.join(random.choice(string.ascii_letters) for _ in range(l))
        dc = dc_encode(text)
        text_from_dc = dc_decode(dc)
        assert text_from_dc == text