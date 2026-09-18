from typing import Any, Optional
from trees.base import BaseNode, KeyValueStore


class BBNode(BaseNode):
    def __init__(self, key: Any, value: Any):
        super().__init__(key, value)
        self.weight: int = 2  # leaf has 1 node, extended weight = 1 + 1 = 2
        self.left: Optional['BBNode'] = None
        self.right: Optional['BBNode'] = None


class WeightBalancedTree(KeyValueStore):
    """
    Weight-Balanced Tree BB[alpha] (Nievergelt & Reingold, 1973; Blum & Mehlhorn, 1980).
    Maintains balance using subtree weights (number of external leaves = size + 1).
    Standard alpha = 0.29, ensuring worst-case O(log n) height with rotations.
    """
    def __init__(self, alpha: float = 0.29):
        super().__init__(f"Weight-Balanced BB[{alpha}]")
        self.alpha: float = alpha
        self.gamma: float = (1.0 - 2.0 * alpha) / (1.0 - alpha)
        self.root: Optional[BBNode] = None
        self._size: int = 0
        self._deleted_flag: bool = False

    def size(self) -> int:
        return self._size

    def _get_root(self) -> Optional[BaseNode]:
        return self.root


    @staticmethod
    def _w(node: Optional[BBNode]) -> int:
        return node.weight if node else 1

    def _update_weight(self, node: BBNode) -> None:
        node.weight = self._w(node.left) + self._w(node.right)

    def _rotate_right(self, t: BBNode) -> BBNode:
        l = t.left
        assert l is not None
        t.left = l.right
        l.right = t
        self._update_weight(t)
        self._update_weight(l)
        self.rotations += 1
        self.structural_modifications += 1
        return l

    def _rotate_left(self, t: BBNode) -> BBNode:
        r = t.right
        assert r is not None
        t.right = r.left
        r.left = t
        self._update_weight(t)
        self._update_weight(r)
        self.rotations += 1
        self.structural_modifications += 1
        return r

    def _rebalance(self, t: Optional[BBNode]) -> Optional[BBNode]:
        if t is None:
            return None
        self._update_weight(t)
        wl = self._w(t.left)
        wr = self._w(t.right)
        wt = t.weight

        if wl > (1.0 - self.alpha) * wt:
            assert t.left is not None
            if self._w(t.left.left) >= self.gamma * wl:
                return self._rotate_right(t)
            else:
                t.left = self._rotate_left(t.left)
                return self._rotate_right(t)
        elif wr > (1.0 - self.alpha) * wt:
            assert t.right is not None
            if self._w(t.right.right) >= self.gamma * wr:
                return self._rotate_left(t)
            else:
                t.right = self._rotate_right(t.right)
                return self._rotate_left(t)
        return t

    def put(self, key: Any, value: Any) -> None:
        def _insert(node: Optional[BBNode]) -> BBNode:
            if node is None:
                self._size += 1
                return BBNode(key, value)
            self.comparisons += 1
            if key < node.key:
                node.left = _insert(node.left)
            elif key > node.key:
                node.right = _insert(node.right)
            else:
                node.value = value
                return node
            return self._rebalance(node)

        self.root = _insert(self.root)

    def get(self, key: Any) -> Optional[Any]:
        curr = self.root
        while curr is not None:
            self.comparisons += 1
            if key == curr.key:
                return curr.value
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def contains(self, key: Any) -> bool:
        return self.get(key) is not None

    def _min_node(self, node: BBNode) -> BBNode:
        curr = node
        while curr.left:
            curr = curr.left
        return curr

    def delete(self, key: Any) -> bool:
        self._deleted_flag = False

        def _delete(node: Optional[BBNode], target_key: Any) -> Optional[BBNode]:
            if node is None:
                return None
            self.comparisons += 1
            if target_key < node.key:
                node.left = _delete(node.left, target_key)
            elif target_key > node.key:
                node.right = _delete(node.right, target_key)
            else:
                self._deleted_flag = True
                if node.left is None and node.right is None:
                    self._size -= 1
                    return None
                elif node.left is None:
                    self._size -= 1
                    return node.right
                elif node.right is None:
                    self._size -= 1
                    return node.left
                else:
                    succ = self._min_node(node.right)
                    node.key = succ.key
                    node.value = succ.value
                    node.right = _delete(node.right, succ.key)

            return self._rebalance(node)

        self.root = _delete(self.root, key)
        return self._deleted_flag
