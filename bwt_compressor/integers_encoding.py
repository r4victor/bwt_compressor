def encode_integers_as_bytes(integers):
    return b''.join(_encode_integer_as_bytes(i) for i in integers)


def _encode_integer_as_bytes(integer):
    bytes_num = 1
    res = []
    while integer >= 256 ** bytes_num - 1:
        integer -= 256 ** bytes_num - 1
        res += b'\xff' * bytes_num
        bytes_num += 1

    res += integer.to_bytes(bytes_num, byteorder='big')
    return bytes(res)


def decode_integers_from_bytes(bytes_):
    integers = [None] * len(bytes_)
    integers_num = 0

    i = 0
    while i < len(bytes_):
        integer, bytes_consumed = _decode_next_integer_from_bytes(bytes_[i:])
        integers[integers_num] = integer
        i += bytes_consumed
        integers_num += 1

    return integers[:integers_num]


def _decode_next_integer_from_bytes(bytes_):
    i = 0
    seen_ffs = 0
    bytes_num_expect = 1
    shift = 0

    while bytes_[i] == 255:
        seen_ffs += 1
        if seen_ffs == bytes_num_expect:
            seen_ffs = 0
            shift += 256 ** bytes_num_expect - 1
            bytes_num_expect += 1
        i += 1
        assert i < len(bytes_)
        
    integer = int.from_bytes(
        bytes_[i-seen_ffs:i-seen_ffs+bytes_num_expect],
        byteorder='big'
    )
    bytes_consumed = i - seen_ffs + bytes_num_expect
    
    return integer + shift, bytes_consumed