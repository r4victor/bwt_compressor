from typing import Optional

import numpy as np


NEW = -1


class Node:
    __slots__ = ['idx', 'value', 'weight', 'left', 'right', 'parent']

    def __init__(
        self, idx: int, weight: int, parent: Optional['Node'],
        left:Optional['Node']=None, right:Optional['Node']=None,
        value:Optional[int]=None
    ):
        self.idx = idx
        self.weight = weight
        self.parent = parent
        self.left = left
        self.right = right
        self.value = value

    def __str__(self):
        return f'({self.idx}, {self.weight}, {self.value}, {self.left}, {self.right})'


class HuffmanTree:
    def __init__(self) -> None:
        root = Node(0, 0, None, value=NEW)
        self.tree = [root]
        self.nodes = {NEW: root}
        self.head = {0: 0}
    
    def add_value(self, value: int) -> list[int]:
        node = self.nodes.get(value, self.nodes[NEW])
        code = self._get_code(node)

        if node.value == NEW:
            node = self.add_new_node(value)
            code.extend(_int_to_bits(value))

        self.increase_weight(node)

        return code

    def _get_code(self, node: Node) -> list[int]:
        code = []
        while node.parent is not None:
            if node.parent.left.idx == node.idx:
                code.append(0)
            else:
                code.append(1)
            node = node.parent
        return list(reversed(code))

    def add_new_node(self, value: int) -> Node:
        node = self.nodes[NEW]
        self.nodes[value] = Node(node.idx + 1, 0, parent=node, value=value)
        self.nodes[NEW] = Node(node.idx + 2, 0, parent=node, value=NEW)
        node.left = self.nodes[value]
        node.right = self.nodes[NEW]
        node.value = None
        self.tree.extend([self.nodes[value], self.nodes[NEW]])
        return node.left

    def increase_weight(self, node: Node) -> None:
        while node is not None:
            same_weight_min_idx = self.head.get(node.weight)

            # Check if we need to swap nodes
            if (same_weight_min_idx is not None and
                same_weight_min_idx < node.idx and
                same_weight_min_idx != node.parent.idx
            ):
                self._swap_nodes(self.tree[same_weight_min_idx], node)
                node = self.tree[same_weight_min_idx]

            if self.tree[node.idx + 1].weight == node.weight:
                # The next node has the same weight
                self.head[node.weight] = node.idx + 1
            elif (self.head.get(node.weight) is not None and
                  self.head[node.weight] == node.idx
            ):
                # no more nodes with this weight
                del self.head[node.weight]

            self.head.setdefault(node.weight + 1, node.idx)

            node.weight += 1
            node = node.parent

    def _swap_nodes(self, node1: Node, node2: Node) -> None:
        node1.left, node2.left = node2.left, node1.left
        node1.right, node2.right = node2.right, node1.right
        if node1.right is not None:
            node1.right.parent = node1
            node1.left.parent = node1
        if node2.right is not None:
            node2.right.parent = node2
            node2.left.parent = node2
        node1.value, node2.value = node2.value, node1.value
        self.nodes[node1.value] = node1
        self.nodes[node2.value] = node2

    def move_to_node(self, code: list[int]) -> tuple[Node, int]:
        node = self.tree[0]
        i = 0
        while node.left is not None:
            if code[i] == 0:
                node = node.left
            else:
                node = node.right
            i += 1
        
        return node, i


def _int_to_bits(n: int) -> list[int]:
    return [n >> i & 1 for i in range(7,-1,-1)]


def huffman_encode(data: bytes) -> bytes:
    ht = HuffmanTree()
    codes = [ht.add_value(byte) for byte in data]

    # We guarantee that the codes are sequences of 0s and 1s
    code = np.concatenate(codes, dtype=np.uint8, casting='unsafe')

    # Prepend code with 0-bits so that its length is a multiple of 8 (byte)
    alignment_length = (8 - (len(code) % 8)) % 8
    aligned_code = np.concatenate(
        [[0] * alignment_length, code],
        dtype=np.uint8, casting='unsafe'
    )
    
    # Pack bits to bytes and prepend alignment_length as the first byte
    packed_code = np.packbits(aligned_code)
    return alignment_length.to_bytes(length=1, byteorder='big') + packed_code.tobytes()


def huffman_decode(huffman_code: bytes) -> bytes:
    arr = np.frombuffer(huffman_code[1:], dtype=np.uint8)
    huffman_code_bits = np.unpackbits(arr)

    ht = HuffmanTree()
    data = []
    consumed = huffman_code[0]
    while consumed < len(huffman_code_bits):
        node, i = ht.move_to_node(huffman_code_bits[consumed:])
        consumed += i
        if node.value == NEW:
            value = int(np.packbits(huffman_code_bits[consumed:consumed+8])[0])
            node = ht.add_new_node(value)
            consumed += 8
        else:
            value = node.value
        
        ht.increase_weight(node)
        data.append(value)
    
    return bytes(data)
