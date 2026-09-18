from typing import Any, Optional
from trees.base import BaseNode, KeyValueStore


class AANode(BaseNode):
    def __init__(self, key: Any, value: Any, level: int = 1):
        super().__init__(key, value)
        self.level: int = level
        self.left: Optional['AANode'] = None
        self.right: Optional['AANode'] = None


class AATree(KeyValueStore):
    """
    AA Tree (Arne Andersson, 1993).
    A variation of the Red-Black Tree that simplifies rebalancing using integer levels
    and restricting horizontal links strictly to the right child.
    """
    def __init__(self):
        super().__init__("AA Tree")
        self.root: Optional[AANode] = None
        self._size: int = 0
        self._deleted_flag: bool = False

    def size(self) -> int:
        return self._size

    def _get_root(self) -> Optional[BaseNode]:
        return self.root


    def _skew(self, node: Optional[AANode]) -> Optional[AANode]:
        """Right rotation if node has a left horizontal link (left.level == node.level)."""
        if node is None or node.left is None:
            return node
        if node.left.level == node.level:
            self.rotations += 1
            self.structural_modifications += 1
            left = node.left
            node.left = left.right
            left.right = node
            return left
        return node

    def _split(self, node: Optional[AANode]) -> Optional[AANode]:
        """Left rotation and level increase if two consecutive right horizontal links exist."""
        if node is None or node.right is None or node.right.right is None:
            return node
        if node.level == node.right.right.level:
            self.rotations += 1
            self.structural_modifications += 1
            right = node.right
            node.right = right.left
            right.left = node
            right.level += 1
            return right
        return node

    def _decrease_level(self, node: AANode) -> AANode:
        """Decrease node level if children levels are too low."""
        left_lvl = node.left.level if node.left else 0
        right_lvl = node.right.level if node.right else 0
        should_be = min(left_lvl, right_lvl) + 1
        if should_be < node.level:
            node.level = should_be
            self.structural_modifications += 1
            if node.right and should_be < node.right.level:
                node.right.level = should_be
        return node

    def put(self, key: Any, value: Any) -> None:
        def _insert(node: Optional[AANode]) -> AANode:
            if node is None:
                self._size += 1
                return AANode(key, value, level=1)
            self.comparisons += 1
            if key < node.key:
                node.left = _insert(node.left)
            elif key > node.key:
                node.right = _insert(node.right)
            else:
                node.value = value
                return node

            node = self._skew(node)
            node = self._split(node)
            return node

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

    def _min_node(self, node: AANode) -> AANode:
        curr = node
        while curr.left:
            curr = curr.left
        return curr

    def delete(self, key: Any) -> bool:
        self._deleted_flag = False

        def _delete(node: Optional[AANode], target_key: Any) -> Optional[AANode]:
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
                    succ = self._min_node(node.right)
                    node.key = succ.key
                    node.value = succ.value
                    node.right = _delete(node.right, succ.key)
                else:
                    pred = self._max_node(node.left)
                    node.key = pred.key
                    node.value = pred.value
                    node.left = _delete(node.left, pred.key)

            if node is None:
                return None

            node = self._decrease_level(node)
            node = self._skew(node)
            if node.right:
                node.right = self._skew(node.right)
                if node.right.right:
                    node.right.right = self._skew(node.right.right)
            node = self._split(node)
            if node.right:
                node.right = self._split(node.right)
            return node

        self.root = _delete(self.root, key)
        return self._deleted_flag

    def _max_node(self, node: AANode) -> AANode:
        curr = node
        while curr.right:
            curr = curr.right
        return curr
