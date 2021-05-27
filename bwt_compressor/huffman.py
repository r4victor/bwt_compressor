import itertools
from typing import Optional
from _pytest._code import code

from bitarray import bitarray, util


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
    
    def add_value(self, value: int) -> bitarray:
        node = self.nodes.get(value, self.nodes[NEW])
        code = self._get_code(node)

        if node.value == NEW:
            code += util.int2ba(value, length=8)
            self.nodes[value] = Node(node.idx + 1, 0, parent=node, value=value)
            self.nodes[NEW] = Node(node.idx + 2, 0, parent=node, value=NEW)
            node.left = self.nodes[value]
            node.right = self.nodes[NEW]
            node.value = None
            self.tree.extend([self.nodes[value], self.nodes[NEW]])
            node = node.left

        while node is not None:
            same_weight_min_idx = self.head.get(node.weight)

            # check if need to swap nodes
            if (same_weight_min_idx is not None and
                same_weight_min_idx < node.idx and
                same_weight_min_idx != node.parent.idx
            ):
                self._swap_nodes(self.tree[same_weight_min_idx], node)
                node = self.tree[same_weight_min_idx]


            if self.tree[node.idx + 1].weight == node.weight:
                # the next node has the same weight
                self.head[node.weight] = node.idx + 1
            elif (self.head.get(node.weight) is not None and
                  self.head[node.weight] == node.idx
            ):
                # no more nodes with this weight
                del self.head[node.weight]

            self.head.setdefault(node.weight + 1, node.idx)

            node.weight += 1
            node = node.parent

        return code

    def _get_code(self, node: Node) -> bitarray:
        code = bitarray()
        while node.parent is not None:
            if node.parent.left.idx == node.idx:
                code.append(0)
            else:
                code.append(1)
            node = node.parent
        code.reverse()
        return code

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

    def get_value(self, code: bitarray) -> Optional[int]:
        node = self.tree[0]

        i = 0
        while node.left is not None:
            if code[i] == 0:
                node = node.left
            else:
                node = node.right
            i += 1
        
        if node.value is None:
            raise ValueError("The code doesn't lead to a leaf node.")

        if node.value == NEW:
            return None, i
        
        return node.value, i


def huffman_encode(data: bytes) -> bytes:
    ht = HuffmanTree()
    codes = [ht.add_value(byte) for byte in data]
    code_bitarray = bitarray(itertools.chain(*codes))
    alignment = (8 - (len(code_bitarray) % 8)) % 8
    code_bitarray = bitarray('0' * alignment) + code_bitarray
    return alignment.to_bytes(length=1, byteorder='big') + code_bitarray.tobytes()


def huffman_decode(huffman_code: bytes) -> bytes:
    huffman_code_bitarray = bitarray()
    huffman_code_bitarray.frombytes(huffman_code[1:])

    ht = HuffmanTree()
    data = []
    consumed = huffman_code[0]
    while consumed < len(huffman_code_bitarray):
        v, i = ht.get_value(huffman_code_bitarray[consumed:])
        consumed += i
        if v is None:
            v = util.ba2int(huffman_code_bitarray[consumed:consumed+8])
            consumed += 8
        
        ht.add_value(v)
        data.append(v)
    
    return bytes(data)

