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


def compress(text):
    assert text.isascii()

    bwt = apply_bwt(text)
    dc = dc_encode(bwt)
    bytes_ = encode_integers_as_bytes(dc)
    return bytes_


def decompress(compressed_text):
    dc = decode_integers_from_bytes(compressed_text)
    bwt = dc_decode(dc)
    text = restore_text_from_bwt(bwt)
    return text


if __name__ == '__main__':
    assert apply_bwt('banana') == 'annb\x00aa'