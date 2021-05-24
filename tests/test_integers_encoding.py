import random

import pytest

from bwt_compressor.integers_encoding import (
    _decode_next_integer_from_bytes,
    decode_integers_from_bytes,
    encode_integers_as_bytes,
    _encode_integer_as_bytes,
)


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
    assert _encode_integer_as_bytes(integer) == expected_bytes


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
        _decode_next_integer_from_bytes(bytes_) ==
        (expected_integer, expected_bytes_consumed)
    )


def test_encode_decode_integers_bytes(max_len=100, max_int=10000000):
    random.seed(20)
    for l in range(max_len):
        integers = [random.randrange(max_int) for _ in range(l)]
        bytes_ = encode_integers_as_bytes(integers)
        integers_decoded = decode_integers_from_bytes(bytes_)
        assert integers_decoded == integers
