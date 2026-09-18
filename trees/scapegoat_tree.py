import math
from typing import Any, Optional, List
from trees.base import BaseNode, KeyValueStore


class ScapegoatNode(BaseNode):
    def __init__(self, key: Any, value: Any):
        super().__init__(key, value)
        self.left: Optional['ScapegoatNode'] = None
        self.right: Optional['ScapegoatNode'] = None


class ScapegoatTree(KeyValueStore):
    """
    Scapegoat Tree (Galperin & Rivest, 1993).
    A self-balancing binary search tree that stores zero balance metadata per node.
    When a path becomes too deep, it finds a 'scapegoat' ancestor and completely
    rebuilds that subtree into a perfectly balanced BST in O(k) time.
    """
    def __init__(self, alpha: float = 0.70):
        super().__init__(f"Scapegoat Tree (alpha={alpha})")
        assert 0.5 < alpha < 1.0, "Alpha must be strictly between 0.5 and 1.0"
        self.alpha: float = alpha
        self.root: Optional[ScapegoatNode] = None
        self._size: int = 0
        self.max_size: int = 0

    def size(self) -> int:
        return self._size

    def _get_root(self) -> Optional[BaseNode]:
        return self.root


    def _subtree_size(self, node: Optional[ScapegoatNode]) -> int:
        if node is None:
            return 0
        return 1 + self._subtree_size(node.left) + self._subtree_size(node.right)

    def _flatten(self, node: Optional[ScapegoatNode], arr: List[ScapegoatNode]) -> None:
        if node is None:
            return
        self._flatten(node.left, arr)
        arr.append(node)
        self._flatten(node.right, arr)

    def _build_balanced(self, arr: List[ScapegoatNode], start: int, end: int) -> Optional[ScapegoatNode]:
        if start > end:
            return None
        mid = (start + end) // 2
        root = arr[mid]
        root.left = self._build_balanced(arr, start, mid - 1)
        root.right = self._build_balanced(arr, mid + 1, end)
        return root

    def _rebuild(self, node: ScapegoatNode) -> ScapegoatNode:
        nodes: List[ScapegoatNode] = []
        self._flatten(node, nodes)
        k = len(nodes)
        self.structural_modifications += k
        return self._build_balanced(nodes, 0, k - 1)

    def put(self, key: Any, value: Any) -> None:
        if self.root is None:
            self.root = ScapegoatNode(key, value)
            self._size = 1
            self.max_size = 1
            return

        # Insert and record ancestors path
        curr = self.root
        path: List[ScapegoatNode] = []
        depth = 0

        while curr is not None:
            self.comparisons += 1
            path.append(curr)
            if key < curr.key:
                if curr.left is None:
                    curr.left = ScapegoatNode(key, value)
                    path.append(curr.left)
                    depth = len(path) - 1
                    self._size += 1
                    break
                curr = curr.left
            elif key > curr.key:
                if curr.right is None:
                    curr.right = ScapegoatNode(key, value)
                    path.append(curr.right)
                    depth = len(path) - 1
                    self._size += 1
                    break
                curr = curr.right
            else:
                curr.value = value
                return

        if self._size > self.max_size:
            self.max_size = self._size

        # Check if depth violates alpha-height-balance: depth > log_{1/alpha}(size)
        h_max = math.floor(math.log(self._size, 1.0 / self.alpha))
        if depth > h_max:
            # Bottom-up search for scapegoat: find first ancestor where child_size > alpha * parent_size
            child_size = 1
            scapegoat_idx = -1
            for i in range(len(path) - 2, -1, -1):
                parent = path[i]
                child = path[i + 1]
                sibling = parent.right if child is parent.left else parent.left
                sibling_size = self._subtree_size(sibling)
                parent_size = 1 + child_size + sibling_size
                if child_size > self.alpha * parent_size:
                    scapegoat_idx = i
                    break
                child_size = parent_size

            if scapegoat_idx != -1:
                scapegoat = path[scapegoat_idx]
                rebuilt_sub = self._rebuild(scapegoat)
                if scapegoat_idx == 0:
                    self.root = rebuilt_sub
                else:
                    ancestor = path[scapegoat_idx - 1]
                    if ancestor.left is scapegoat:
                        ancestor.left = rebuilt_sub
                    else:
                        ancestor.right = rebuilt_sub

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

    def _min_node(self, node: ScapegoatNode) -> ScapegoatNode:
        curr = node
        while curr.left:
            curr = curr.left
        return curr

    def delete(self, key: Any) -> bool:
        if self.root is None:
            return False

        deleted = False

        def _delete(node: Optional[ScapegoatNode], target: Any) -> Optional[ScapegoatNode]:
            nonlocal deleted
            if node is None:
                return None
            self.comparisons += 1
            if target < node.key:
                node.left = _delete(node.left, target)
            elif target > node.key:
                node.right = _delete(node.right, target)
            else:
                deleted = True
                if node.left is None:
                    return node.right
                elif node.right is None:
                    return node.left
                else:
                    succ = self._min_node(node.right)
                    node.key = succ.key
                    node.value = succ.value
                    node.right = _delete(node.right, succ.key)
            return node

        self.root = _delete(self.root, key)
        if deleted:
            self._size -= 1
            # Check delete rebuild condition
            if self._size < self.alpha * self.max_size and self._size > 0:
                self.root = self._rebuild(self.root)
                self.max_size = self._size
            elif self._size == 0:
                self.max_size = 0
            return True
        return False
