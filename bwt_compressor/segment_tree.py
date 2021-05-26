
class SegmentTreeRecursive:
    """
    Straightforward but inefficient implementation as described in
    https://www.geeksforgeeks.org/segment-tree-set-1-sum-of-given-range/
    """
    def __init__(self, leafs):
        self.leafs_num = len(leafs)
        self.size = self._calculate_segment_tree_size(len(leafs))
        self.tree = [None] * self.size
        self._init_segment_tree(leafs, 0, 0, len(leafs))

    @staticmethod
    def _calculate_segment_tree_size(n):
        x = 1
        while x < n:
            x <<= 1
        return 2 * x -1

    def _init_segment_tree(self, leafs, node_idx, l , r):
        if len(leafs) == 0:
            return 0
        if len(leafs) == 1:
            self.tree[node_idx] = [l, r, leafs[0]]
            return leafs[0]
        m = (len(leafs) + 1) // 2
        lw = self._init_segment_tree(leafs[:m], 2 * node_idx + 1, l, l+m)
        rw = self._init_segment_tree(leafs[m:], 2 * node_idx + 2, l+m, r)
        w = lw + rw
        self.tree[node_idx] = [l, r, w]
        return w

    def get_sum(self, l, r, node_idx=0):
        if self.tree[node_idx] is None:
            return 0
        if l <= self.tree[node_idx][0] and self.tree[node_idx][1] <= r:
            return self.tree[node_idx][2]
        if self.tree[node_idx][1] <= l or self.tree[node_idx][0] >= r:
            return 0
        if 2 * node_idx + 1 >= len(self.tree):
            return 0
        return self.get_sum(l, r, 2*node_idx + 1) + self.get_sum(l, r, 2*node_idx + 2)

    def update(self, idx, diff, node_idx=0):
        if self.tree[node_idx] is None:
            return
        if self.tree[node_idx][0] <= idx < self.tree[node_idx][1]:
            self.tree[node_idx][2] = self.tree[node_idx][2] + diff
            if 2 * node_idx + 1 >= len(self.tree):
                return
            self.update(idx, diff, 2 * node_idx + 1)
            self.update(idx, diff, 2 * node_idx + 2)


class SegmentTree:
    """
    Efficent implementation as described in
    https://codeforces.com/blog/entry/18051
    """
    def __init__(self, leafs):
        self.leafs_num = len(leafs)
        self.tree = [0] * (2 * self.leafs_num)
        self._init_segment_tree(leafs)

    def _init_segment_tree(self, leafs):
        self.tree = [0] * self.leafs_num + leafs
        for i in range(self.leafs_num - 1, 0, -1):
            self.tree[i] = self.tree[i<<1] + self.tree[i<<1 | 1]

    def update(self, idx, diff):
        tree_idx = self.leafs_num + idx
        self.tree[tree_idx] += diff
        while tree_idx != 0:
            tree_idx >>= 1
            self.tree[tree_idx] += diff

    def get_sum(self, l, r):
        res = 0
        l += self.leafs_num
        r += self.leafs_num

        while l < r:
            if l % 2 == 1:
                res += self.tree[l]
                l += 1
            if r % 2 == 1:
                r -= 1
                res += self.tree[r]
            l //= 2
            r //= 2
        
        return res
