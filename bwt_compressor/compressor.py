import numpy as np

from bwt_compressor.integers_encoding import (
    decode_integers_from_bytes,
    encode_integers_as_bytes
)

from bwt_compressor.bwt import apply_bwt, restore_text_from_bwt
from bwt_compressor.dc import dc_encode, dc_decode
from bwt_compressor.integers_encoding import (
    encode_integers_as_bytes,
    decode_integers_from_bytes
)
from bwt_compressor.huffman import huffman_encode, huffman_decode


def compress(text):
    assert text.isascii()

    bwt = apply_bwt(text)
    dc = dc_encode(bwt)
    bytes_ = encode_integers_as_bytes(dc)
    huffman_code = huffman_encode(bytes_)
    return huffman_code


def decompress(compressed_text):
    dc_as_bytes = huffman_decode(compressed_text)
    bytes_ndarray = np.frombuffer(dc_as_bytes, dtype=np.uint8)
    dc = decode_integers_from_bytes(bytes_ndarray)
    bwt = dc_decode(dc)
    text = restore_text_from_bwt(bwt)
    return text