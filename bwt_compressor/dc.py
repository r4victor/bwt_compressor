from bwt_compressor.common import (
    ALPHABET_SIZE,
    TERMINATOR_SYMBOL
)
from bwt_compressor.segment_tree import SegmentTree


def dc_encode(text):
    alphabet_and_text = _get_alphabet() + text
    char_distances = _compute_char_distances(alphabet_and_text)
    char_distances_reduced = _reduce_char_distances(alphabet_and_text, char_distances)
    dc = _remove_redundant_ones(char_distances, char_distances_reduced)
    return [len(text)] + dc


def _get_alphabet():
    return ''.join(chr(i) for i in range(ALPHABET_SIZE))


def _compute_char_distances(text):
    char_distances = [0] * len(text)
    last_seen_indices = list(range(ALPHABET_SIZE))
    for i in range(ALPHABET_SIZE, len(text)):
        char = text[i]
        last_seen_index = last_seen_indices[ord(char)]
        distance = i - last_seen_index
        char_distances[last_seen_index] = distance
        last_seen_indices[ord(char)] = i
    return char_distances


def _reduce_char_distances(alphabet_and_text, char_distances):
    text_length = len(alphabet_and_text) - ALPHABET_SIZE
    known_chars_st = SegmentTree([1] * ALPHABET_SIZE + [0] * text_length)
    reduced_char_distances = [None] * len(char_distances)
    for i, d in enumerate(char_distances):
        reduced_char_distances[i] = d - known_chars_st.get_sum(i+1, i + d)
        known_chars_st.update(i+d, 1)
    return reduced_char_distances


def _remove_redundant_ones(char_distances, char_distances_reduced):
    res = char_distances_reduced.copy()
    for i, d in enumerate(char_distances):
        if d == 1:
            res[i] = None
    return [d for d in res if d is not None]


def dc_decode(dc):
    text_length = dc[0]
    text = list(_get_alphabet()) + [None] * text_length
    known_chars_st = SegmentTree([1] * ALPHABET_SIZE + [0] * text_length)

    i = 0
    for d in dc[1:]:
        # Restore consecutive chars
        while i < len(text) - 1 and text[i+1] is None:
            text[i+1] = text[i]
            i += 1

        if d == 0:
            i += 1
            continue
        
        # Find the dth empty index.
        # Go to the i + d index first, then
        # calculate how many indices in between aren't empty and
        # find the known_chars_num'th empty index.
        # This is an optimization.
        known_chars_num = known_chars_st.get_sum(i + 1, i + d) + 1
        dth_empty_index = _find_kth_empty_index(text, i + d, known_chars_num)

        text[dth_empty_index] = text[i]
        known_chars_st.update(dth_empty_index, 1)

        i += 1

    return ''.join(text[ALPHABET_SIZE:])


def _find_kth_empty_index(text, start_post, k):
    i = 0
    while True:
        if text[start_post + i] is None:
            k -= 1
        if k == 0:
            break
        i += 1
    return start_post + i

