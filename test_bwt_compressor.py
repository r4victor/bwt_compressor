import itertools
import random
import string

import pytest


from bwt_compressor import (
    ALPHABET_SIZE,
    apply_bwt,
    build_suffix_array,
    compress,
    dc_decode,
    dc_encode,
    decode_integers_from_bytes,
    decode_next_integer_from_bytes,
    decompress,
    encode_integer_as_bytes,
    encode_integers_as_bytes,
    get_alphabet,
    reduce_char_distances,
    restore_text_from_bwt,
    compute_sorting_permutation,
    compute_sorting_permutation_inverse,
    compute_char_distances
)


@pytest.fixture
def fixture_dummy():
    pass


def test_compress_decompress():
    random.seed(20)
    for l in itertools.chain(range(100), range(1000, 1010)):
        text = ''.join(random.choice(string.ascii_letters) for _ in range(l))
        compressed_text = compress(text)
        decompressed_text = decompress(compressed_text)
        assert decompressed_text == text


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
    assert build_suffix_array(text) == expected_suffix_array


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
    text = get_alphabet() + text
    alphabet_char_distances = [0] * ALPHABET_SIZE
    for i, c in enumerate(text[ALPHABET_SIZE:]):
        if alphabet_char_distances[ord(c)] == 0:
            alphabet_char_distances[ord(c)] = ALPHABET_SIZE - ord(c) + i
    assert (
        compute_char_distances(text) ==
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
    text = get_alphabet() + text
    char_distances = compute_char_distances(text)
    reduced_char_distances = reduce_char_distances(text, char_distances)
    assert (
        reduce_char_distances(text, char_distances)[ALPHABET_SIZE:] ==
        expected_reduced_char_distances
    )


def test_reduce_char_distances_with_alphabet():
    text = 'AZ\x00'
    alphabet = get_alphabet()
    alphabet_char_distances = [0] * len(alphabet)
    alphabet_char_distances[0] = len(alphabet) + len(text) - 1
    alphabet_char_distances[ord('A')] = 191
    alphabet_char_distances[ord('Z')] = 167
    expected_reduced_alphabet_char_distances = [0] * len(alphabet)
    expected_reduced_alphabet_char_distances[0] = len(text)
    expected_reduced_alphabet_char_distances[ord('A')] = 1
    expected_reduced_alphabet_char_distances[ord('Z')] = 1
    assert (
        reduce_char_distances(alphabet + text, alphabet_char_distances + [0,0,0]) ==
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


@pytest.mark.parametrize(
    ['integer', 'expected_bytes'],
    [
        (0, b'\x00'),
        (ord('a'), b'a'),
        (255, b'\xff\x00\x00'),
        (256, b'\xff\x00\x01'),
        (255 + 256 ** 2 - 1, b'\xff\xff\xff\x00\x00\x00')
    ]
)
def test_encode_integer_as_bytes(integer, expected_bytes):
    assert encode_integer_as_bytes(integer) == expected_bytes


@pytest.mark.parametrize(
    ['bytes_', 'expected_integer', 'expected_bytes_consumed'],
    [
        (b'\x00', 0, 1),
        (b'a', ord('a'), 1),
        (b'ab', ord('a'), 1),
        (b'\xfe', 254, 1),
        (b'\xff\x00\x00', 255, 3),
        (b'\xff\x00\x01', 256, 3),
    ]
)
def test_dencode_next_integer_from_bytes(
    bytes_, expected_integer, expected_bytes_consumed
):
    assert (
        decode_next_integer_from_bytes(bytes_) ==
        (expected_integer, expected_bytes_consumed)
    )


def test_encode_decode_integers_bytes(max_len=100, max_int=10000000):
    random.seed(20)
    for l in range(max_len):
        integers = [random.randrange(max_int) for _ in range(l)]
        bytes_ = encode_integers_as_bytes(integers)
        integers_decoded = decode_integers_from_bytes(bytes_)
        assert integers_decoded == integers



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
        compute_sorting_permutation(text) ==
        expected_sorting_permutation_inverse
    )


def test_compute_sorting_permutation_inverse_random(max_len=20):
    random.seed(17)
    for l in range(max_len):
        text = ''.join(random.choice(string.ascii_letters) for _ in range(l))
        sorting_permutation_inverse = compute_sorting_permutation_inverse(text)
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
        compute_sorting_permutation(text) ==
        expected_sorting_permutation
    )