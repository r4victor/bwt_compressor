from bwt_compressor.common import (
    ALPHABET_SIZE,
    TERMINATOR_SYMBOL
)


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


def _reduce_char_distances(text, char_distances):
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


def _remove_redundant_ones(char_distances, char_distances_reduced):
    res = char_distances_reduced.copy()
    for i, d in enumerate(char_distances):
        if d == 1:
            res[i] = None
    return [d for d in res if d is not None]


def dc_decode(dc):
    text_length = dc[0]
    text = list(_get_alphabet()) + [None] * text_length
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
