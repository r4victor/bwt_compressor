import itertools


ALPHABET_SIZE = 256
TERMINATOR_SYMBOL = '\x00'


def compress(text):
    assert text.isascii()

    bwt = apply_bwt(text)
    dc = dc_encode(bwt)
    bytes_ = encode_integers_as_bytes(dc)

    return bytes_


def apply_bwt(text):
    assert TERMINATOR_SYMBOL not in text

    suffix_array = build_suffix_array(text)

    bwt = [None] * len(text)
    for suffix_start_index, sorted_position in enumerate(suffix_array):
        if suffix_start_index != 0:
            bwt[sorted_position] = text[suffix_start_index - 1]
        else:
            bwt[sorted_position] = TERMINATOR_SYMBOL

    first_char = text[-1] if len(text) > 0 else TERMINATOR_SYMBOL

    return first_char + ''.join(bwt)


def build_suffix_array(text):
    return build_suffix_array_naive(text)


def build_suffix_array_naive(text):
    """
    Construct the suffix array in O(n^2logn).
    """
    n = len(text)

    # build pairs (suffix, suffix start index)
    suffixes = ((text[i:], i) for i in range(n))
    sorted_suffixes = list(sorted(suffixes))

    suffix_array = [None] * n
    for sorted_position in range(n):
        suffix_start_index = sorted_suffixes[sorted_position][1]
        suffix_array[suffix_start_index] = sorted_position

    return suffix_array


def dc_encode(text):
    alphabet_and_text = get_alphabet() + text
    char_distances = compute_char_distances(alphabet_and_text)
    char_distances_reduced = reduce_char_distances(alphabet_and_text, char_distances)
    dc = remove_redundant_ones(char_distances, char_distances_reduced)
    return [len(text)] + dc


def get_alphabet():
    return ''.join(chr(i) for i in range(ALPHABET_SIZE))


def compute_char_distances(text):
    char_distances = [0] * len(text)
    last_seen_indices = list(range(ALPHABET_SIZE))
    for i in range(ALPHABET_SIZE, len(text)):
        char = text[i]
        last_seen_index = last_seen_indices[ord(char)]
        distance = i - last_seen_index
        char_distances[last_seen_index] = distance
        last_seen_indices[ord(char)] = i
    return char_distances


def reduce_char_distances(text, char_distances):
    reduced_char_distances = char_distances.copy()
    last_char_indices = list(range(ALPHABET_SIZE))
    next_char_distances = char_distances[:ALPHABET_SIZE]
    for i in range(ALPHABET_SIZE):
        if reduced_char_distances[i] > 0:
            reduced_char_distances[i] -= (ALPHABET_SIZE - i - 1)

    for i, distance in enumerate(char_distances):
        char = text[i]
        for last_char_index, next_char_distance in zip(last_char_indices, next_char_distances):
            if (next_char_distance > 0 and
                last_char_index < i and
                i < last_char_index + next_char_distance < i + distance
            ):
                reduced_char_distances[i] -= 1

        next_char_distances[ord(char)] = distance
        last_char_indices[ord(char)] = i
    return reduced_char_distances


def remove_redundant_ones(char_distances, char_distances_reduced):
    res = char_distances_reduced.copy()
    for i, d in enumerate(char_distances):
        if d == 1:
            res[i] = None
    return [d for d in res if d is not None]


def encode_integers_as_bytes(integers):
    return b''.join(encode_integer_as_bytes(i) for i in integers)


def encode_integer_as_bytes(integer):
    bytes_num = 1
    res = []
    while integer >= 256 ** bytes_num - 1:
        integer -= 256 ** bytes_num - 1
        res += b'\xff' * bytes_num
        bytes_num += 1

    res += integer.to_bytes(bytes_num, byteorder='big')
    return bytes(res)


def decode_integers_from_bytes(bytes_):
    integers = []
    i = 0
    while i < len(bytes_):
        integer, bytes_consumed = decode_next_integer_from_bytes(bytes_[i:])
        integers.append(integer)
        i += bytes_consumed

    return integers


def decode_next_integer_from_bytes(bytes_):
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


def decompress(compressed_text):
    dc = decode_integers_from_bytes(compressed_text)
    bwt = dc_decode(dc)
    text = restore_text_from_bwt(bwt)
    return text


def dc_decode(dc):
    text_length = dc[0]
    text = list(get_alphabet()) + [None] * text_length
    next_empty_index = ALPHABET_SIZE

    i = 0
    for d in dc[1:]:
        # restore consecutive chars
        while i < len(text) - 1 and text[i+1] == None:
            text[i+1] = text[i]
            i += 1

        if d == 0:
            i += 1
            continue
        
        # find the dth empty index
        dth_empty_index = next_empty_index
        while True:
            if text[dth_empty_index] == None:
                d -= 1
            
            if d == 0:
                break

            dth_empty_index += 1

        text[dth_empty_index] = text[i]
        
        # update the next empty index
        while next_empty_index < len(text) and text[next_empty_index] != None:
            next_empty_index += 1

        i += 1

    return ''.join(text[ALPHABET_SIZE:])
        


def restore_text_from_bwt(bwt):
    sorting_permutation_inverse = compute_sorting_permutation_inverse(bwt)
    text = [None] * (len(bwt) - 1)
    cur_pos = bwt.find(TERMINATOR_SYMBOL)
    for i in range(len(text)):
        cur_pos = sorting_permutation_inverse[cur_pos]
        text[i] = bwt[cur_pos]
    return ''.join(text)


def compute_sorting_permutation_inverse(text):
    sorting_permutation = compute_sorting_permutation(text)
    return compute_inverse_permutation(sorting_permutation)


def compute_sorting_permutation(text):
    counters = get_chars_counters(text)
    start_positions = get_chars_start_positions(counters)
    sorting_permutation = [None] * len(text)
    for i, c in enumerate(text):
        sorting_permutation[i] = start_positions[ord(c)]
        start_positions[ord(c)] += 1
    return sorting_permutation


def get_chars_counters(text):
    counters = [0] * ALPHABET_SIZE
    for c in text:
        counters[ord(c)] += 1
    return counters


def get_chars_start_positions(counters):
    return list(itertools.accumulate([0] + counters))[:-1]


def compute_inverse_permutation(permutation):
    inverse_permutation = [None] * len(permutation)
    for i, j in enumerate(permutation):
        inverse_permutation[j] = i
    return inverse_permutation


if __name__ == '__main__':
    assert apply_bwt('banana') == 'annb\x00aa'