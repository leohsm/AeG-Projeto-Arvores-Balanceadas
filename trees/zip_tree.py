import random
from typing import Any, Optional, Tuple
from trees.base import BaseNode, KeyValueStore


class ZipNode(BaseNode):
    def __init__(self, key: Any, value: Any, rank: int):
        super().__init__(key, value)
        self.rank: int = rank
        self.left: Optional['ZipNode'] = None
        self.right: Optional['ZipNode'] = None


class ZipTree(KeyValueStore):
    """
    Zip Tree (Robert E. Tarjan, Caleb Levy, Stephen Tsz-Kin Wong, 2019/2021).
    A randomized binary search tree isomorphic to skip lists.
    Nodes are assigned geometric ranks and balanced via zip and unzip operations.
    """
    def __init__(self, seed: Optional[int] = None):
        super().__init__("Zip Tree")
        self.root: Optional[ZipNode] = None
        self._size: int = 0
        self._rng = random.Random(seed)

    def size(self) -> int:
        return self._size

    def _get_root(self) -> Optional[BaseNode]:
        return self.root


    def _random_rank(self) -> int:
        """Draw rank from geometric distribution with p = 0.5."""
        r = 0
        while self._rng.random() < 0.5:
            r += 1
        return r

    def _unzip(self, node: Optional[ZipNode], key: Any) -> Tuple[Optional[ZipNode], Optional[ZipNode]]:
        """
        Unzips a subtree into two subtrees: (keys < key, keys > key).
        """
        if node is None:
            return None, None
        self.comparisons += 1
        if node.key < key:
            left_sub, right_sub = self._unzip(node.right, key)
            node.right = left_sub
            self.structural_modifications += 1
            return node, right_sub
        else:
            left_sub, right_sub = self._unzip(node.left, key)
            node.left = right_sub
            self.structural_modifications += 1
            return left_sub, node

    def _zip(self, left: Optional[ZipNode], right: Optional[ZipNode]) -> Optional[ZipNode]:
        """
        Zips two subtrees together, where all keys in left < all keys in right.
        """
        if left is None:
            return right
        if right is None:
            return left

        self.structural_modifications += 1
        # Left has priority if left.rank >= right.rank
        if left.rank >= right.rank:
            left.right = self._zip(left.right, right)
            return left
        else:
            right.left = self._zip(left, right.left)
            return right

    def put(self, key: Any, value: Any) -> None:
        # A candidate with a high random rank may outrank an ancestor before the
        # insertion walk reaches an equal key.  Resolve updates first so the
        # existing node keeps its rank and duplicate keys are impossible.
        existing = self.root
        while existing is not None:
            self.comparisons += 1
            if key == existing.key:
                existing.value = value
                return
            existing = existing.left if key < existing.key else existing.right

        rank = self._random_rank()
        parent: Optional[ZipNode] = None
        curr = self.root

        # Follow the search path until the new node outranks the current node.
        # Existing keys have already been handled above.
        while curr is not None:
            self.comparisons += 1
            if key == curr.key:
                curr.value = value
                return
            outranks = rank > curr.rank or (rank == curr.rank and key < curr.key)
            if outranks:
                break
            parent = curr
            curr = curr.left if key < curr.key else curr.right

        new_node = ZipNode(key, value, rank)
        new_node.left, new_node.right = self._unzip(curr, key)
        if parent is None:
            self.root = new_node
        elif key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node

        self._size += 1
        self.structural_modifications += 1

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

    def delete(self, key: Any) -> bool:
        deleted = False

        def _delete(node: Optional[ZipNode]) -> Optional[ZipNode]:
            nonlocal deleted
            if node is None:
                return None

            self.comparisons += 1
            if key < node.key:
                node.left = _delete(node.left)
                return node
            elif key > node.key:
                node.right = _delete(node.right)
                return node
            else:
                deleted = True
                return self._zip(node.left, node.right)

        self.root = _delete(self.root)
        if deleted:
            self._size -= 1
            return True
        return False
