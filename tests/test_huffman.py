import random
import string

from bitarray import bitarray
import pytest


from bwt_compressor.huffman import HuffmanTree, huffman_encode, huffman_decode


def test_huffman_add_value_move_to_node():
    ht = HuffmanTree()
    assert ht.add_value(1) == [0,0,0,0,0,0,0,1]
    assert ht.add_value(2) == [1,0,0,0,0,0,0,1,0]
    assert ht.add_value(2) == [1, 0]
    assert ht.add_value(2) == [0]
    assert ht.add_value(1) == [1, 0]

    assert ht.move_to_node([0])[0].value == 2
    assert ht.move_to_node([1, 0])[0].value == 1


# def test_huffman_incomplete_code_raises_error():
#     ht = HuffmanTree()
#     ht.add_value(1)
#     ht.add_value(2)
#     with pytest.raises(ValueError):
#         ht.get_value(bitarray('1'))


def test_huffman_encode_decode(max_len=50):
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

