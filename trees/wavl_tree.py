from typing import Any, Optional
from trees.base import BaseNode, KeyValueStore


class WAVLNode(BaseNode):
    def __init__(self, key: Any, value: Any, rank: int = 0):
        super().__init__(key, value)
        self.rank: int = rank
        self.left: Optional['WAVLNode'] = None
        self.right: Optional['WAVLNode'] = None
        self.parent: Optional['WAVLNode'] = None


class WAVLTree(KeyValueStore):
    """
    Weak AVL (WAVL) Tree (Bernhard Haeupler, Siddhartha Sen, Robert E. Tarjan, 2015).
    A rank-balanced binary search tree that bounds height to <= 1.44 log2(n).
    Guarantees at most 2 rotations on insertion AND at most 2 rotations on deletion.
    """
    def __init__(self):
        super().__init__("WAVL Tree")
        self.root: Optional[WAVLNode] = None
        self._size: int = 0

    def size(self) -> int:
        return self._size

    def _get_root(self) -> Optional[BaseNode]:
        return self.root


    @staticmethod
    def _rank(node: Optional[WAVLNode]) -> int:
        return node.rank if node is not None else -1

    def _diff(self, parent: Optional[WAVLNode], child: Optional[WAVLNode]) -> int:
        if parent is None:
            return 0
        return self._rank(parent) - self._rank(child)

    @staticmethod
    def _is_leaf(node: Optional[WAVLNode]) -> bool:
        return node is not None and node.left is None and node.right is None

    def _rotate_right(self, p: WAVLNode) -> WAVLNode:
        x = p.left
        assert x is not None
        p.left = x.right
        if x.right:
            x.right.parent = p
        x.right = p
        x.parent = p.parent
        p.parent = x
        if x.parent is None:
            self.root = x
        elif x.parent.left is p:
            x.parent.left = x
        else:
            x.parent.right = x
        self.rotations += 1
        self.structural_modifications += 1
        return x

    def _rotate_left(self, p: WAVLNode) -> WAVLNode:
        x = p.right
        assert x is not None
        p.right = x.left
        if x.left:
            x.left.parent = p
        x.left = p
        x.parent = p.parent
        p.parent = x
        if x.parent is None:
            self.root = x
        elif x.parent.left is p:
            x.parent.left = x
        else:
            x.parent.right = x
        self.rotations += 1
        self.structural_modifications += 1
        return x

    def put(self, key: Any, value: Any) -> None:
        if self.root is None:
            self.root = WAVLNode(key, value, rank=0)
            self._size = 1
            return

        curr = self.root
        parent = None
        while curr is not None:
            self.comparisons += 1
            if key == curr.key:
                curr.value = value
                return
            parent = curr
            if key < curr.key:
                curr = curr.left
            else:
                curr = curr.right

        new_node = WAVLNode(key, value, rank=0)
        new_node.parent = parent
        if key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node
        self._size += 1

        # Rebalance after insertion
        self._rebalance_insert(new_node)

    def _rebalance_insert(self, x: WAVLNode) -> None:
        """
        Bottom-up rebalancing after inserting leaf x.
        Terminates with at most 2 rotations.
        """
        while x.parent is not None:
            p = x.parent
            if self._diff(p, x) != 0:
                break

            sibling = p.right if p.left is x else p.left
            if self._diff(p, sibling) == 1:
                # Case 1: Promote parent
                p.rank += 1
                self.structural_modifications += 1
                x = p  # continue upwards
            else:
                # Case 2: Sibling diff is 2 -> Rotation needed
                if p.left is x:
                    # Left child violation
                    if self._diff(x, x.left) == 1:
                        # Subcase 2a: Single rotation right
                        self._rotate_right(p)
                        p.rank -= 1
                        self.structural_modifications += 1
                    else:
                        # Subcase 2b: Double rotation left-right
                        w = x.right
                        assert w is not None
                        self._rotate_left(x)
                        self._rotate_right(p)
                        w.rank += 1
                        x.rank -= 1
                        p.rank -= 1
                        self.structural_modifications += 3
                else:
                    # Right child violation
                    if self._diff(x, x.right) == 1:
                        # Subcase 2a: Single rotation left
                        self._rotate_left(p)
                        p.rank -= 1
                        self.structural_modifications += 1
                    else:
                        # Subcase 2b: Double rotation right-left
                        w = x.left
                        assert w is not None
                        self._rotate_right(x)
                        self._rotate_left(p)
                        w.rank += 1
                        x.rank -= 1
                        p.rank -= 1
                        self.structural_modifications += 3
                break

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

    def _find_node(self, key: Any) -> Optional[WAVLNode]:
        curr = self.root
        while curr is not None:
            self.comparisons += 1
            if key == curr.key:
                return curr
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def _min_node(self, node: WAVLNode) -> WAVLNode:
        curr = node
        while curr.left:
            curr = curr.left
        return curr

    def delete(self, key: Any) -> bool:
        node = self._find_node(key)
        if node is None:
            return False

        # If node has two children, swap with successor
        if node.left is not None and node.right is not None:
            succ = self._min_node(node.right)
            node.key = succ.key
            node.value = succ.value
            node = succ

        # Now node has at most one child
        child = node.left if node.left is not None else node.right
        parent = node.parent

        if child is not None:
            child.parent = parent

        if parent is None:
            self.root = child
        elif parent.left is node:
            parent.left = child
        else:
            parent.right = child

        self._size -= 1

        # Rebalance from parent or child
        if parent is not None:
            self._rebalance_delete(parent, child)
        elif self.root is not None and self._is_leaf(self.root):
            self.root.rank = 0

        return True

    def _rebalance_delete(self, p: WAVLNode, x: Optional[WAVLNode]) -> None:
        """
        Bottom-up rebalancing after deletion.
        Restores rank differences to {1, 2} and eliminates (2, 2)-leaves.
        Terminates with at most 2 rotations.
        """
        while p is not None:
            # Check if p became a (2, 2)-leaf
            if self._is_leaf(p) and p.rank == 1:
                p.rank = 0
                self.structural_modifications += 1
                x = p
                p = p.parent
                continue

            # Identify if child x has rank diff 3
            # Or determine which child is deficient
            diff_left = self._diff(p, p.left)
            diff_right = self._diff(p, p.right)

            if diff_left <= 2 and diff_right <= 2:
                break

            if diff_left == 3:
                # Left child deficient, sibling is right child
                y = p.right
                assert y is not None
                diff_y = diff_right
                if diff_y == 2:
                    # Case 1: Demote parent
                    p.rank -= 1
                    self.structural_modifications += 1
                    x = p
                    p = p.parent
                elif diff_y == 1:
                    # Sibling has rank diff 1
                    diff_yl = self._diff(y, y.left)
                    diff_yr = self._diff(y, y.right)
                    if diff_yl == 2 and diff_yr == 2:
                        # Case 2: Double demote
                        p.rank -= 1
                        y.rank -= 1
                        self.structural_modifications += 2
                        x = p
                        p = p.parent
                    else:
                        # Case 3: Rotation
                        if diff_yr == 1:
                            # Single left rotation
                            self._rotate_left(p)
                            y.rank = p.rank
                            p.rank -= 1
                            self.structural_modifications += 2
                            if self._is_leaf(p) and p.rank == 1:
                                p.rank = 0
                        else:
                            # Double right-left rotation
                            w = y.left
                            assert w is not None
                            self._rotate_right(y)
                            self._rotate_left(p)
                            w.rank = p.rank
                            p.rank -= 2
                            y.rank -= 1
                            self.structural_modifications += 3
                            if self._is_leaf(p) and p.rank == 1:
                                p.rank = 0
                        break
            elif diff_right == 3:
                # Right child deficient, sibling is left child
                y = p.left
                assert y is not None
                diff_y = diff_left
                if diff_y == 2:
                    # Case 1: Demote parent
                    p.rank -= 1
                    self.structural_modifications += 1
                    x = p
                    p = p.parent
                elif diff_y == 1:
                    # Sibling has rank diff 1
                    diff_yl = self._diff(y, y.left)
                    diff_yr = self._diff(y, y.right)
                    if diff_yl == 2 and diff_yr == 2:
                        # Case 2: Double demote
                        p.rank -= 1
                        y.rank -= 1
                        self.structural_modifications += 2
                        x = p
                        p = p.parent
                    else:
                        # Case 3: Rotation
                        if diff_yl == 1:
                            # Single right rotation
                            self._rotate_right(p)
                            y.rank = p.rank
                            p.rank -= 1
                            self.structural_modifications += 2
                            if self._is_leaf(p) and p.rank == 1:
                                p.rank = 0
                        else:
                            # Double left-right rotation
                            w = y.right
                            assert w is not None
                            self._rotate_left(y)
                            self._rotate_right(p)
                            w.rank = p.rank
                            p.rank -= 2
                            y.rank -= 1
                            self.structural_modifications += 3
                            if self._is_leaf(p) and p.rank == 1:
                                p.rank = 0
                        break
            else:
                break
