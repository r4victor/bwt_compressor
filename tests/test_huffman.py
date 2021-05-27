import random
import string

from bitarray import bitarray
import pytest


from bwt_compressor.huffman import HuffmanTree, huffman_encode, huffman_decode


def test_huffman_add_value_get_value():
    ht = HuffmanTree()
    r = ht.add_value(1)
    assert r == bitarray(f'{1:08b}')
    r = ht.add_value(2)
    assert r == bitarray(f'1{2:08b}')
    r = ht.add_value(2)
    assert r == bitarray('10')
    r = ht.add_value(2)
    assert r == bitarray('0')
    r = ht.add_value(1)
    assert r == bitarray('10')

    assert ht.get_value(bitarray('0')) == (2, 1)
    assert ht.get_value(bitarray('10')) == (1, 2)


# def test_huffman_incomplete_code_raises_error():
#     ht = HuffmanTree()
#     ht.add_value(1)
#     ht.add_value(2)
#     with pytest.raises(ValueError):
#         ht.get_value(bitarray('1'))


def test_huffman_encode_decode(max_len=100):
    random.seed(20)
    for l in range(1, max_len):
        data = ''.join(random.choice(string.ascii_letters) for _ in range(l)).encode()
        huffman_code = huffman_encode(data)
        # assert huffman_code is data
        decoded_data = huffman_decode(huffman_code)
        assert decoded_data == data


def test_huffman_encode():
    data = b'vvBfO'
    expected_huffman_code = bitarray(
        f'{1:08b}0{118:08b}01{66:08b}11{102:08b}111{79:08b}'
    ).tobytes()
    assert huffman_encode(data) == expected_huffman_code


def test_huffman_decode():
    huffman_code = bitarray(
        f'{1:08b}0{118:08b}01{66:08b}11{102:08b}111{79:08b}'
    ).tobytes()
    expected_data = b'vvBfO'
    assert huffman_decode(huffman_code) == expected_data

