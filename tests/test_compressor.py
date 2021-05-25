import itertools
import random
import string

import pytest


from bwt_compressor.compressor import (
    compress,
    decompress
)


def test_compress_decompress():
    random.seed(20)
    for l in itertools.chain(range(100), range(1000, 1010)):
        text = ''.join(random.choice(string.ascii_letters) for _ in range(l))
        compressed_text = compress(text)
        decompressed_text = decompress(compressed_text)
        assert decompressed_text == text


