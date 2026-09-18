from typing import Any, Optional
from trees.base import BaseNode, KeyValueStore


class SplayNode(BaseNode):
    def __init__(self, key: Any, value: Any):
        super().__init__(key, value)
        self.left: Optional['SplayNode'] = None
        self.right: Optional['SplayNode'] = None


class SplayTree(KeyValueStore):
    """
    Splay Tree (Sleator & Tarjan, 1985).
    Self-adjusting binary search tree using top-down splaying.
    Recently accessed elements are brought to the root via amortized O(log n) rotations.
    """
    def __init__(self):
        super().__init__("Splay Tree")
        self.root: Optional[SplayNode] = None
        self._size: int = 0
        self._dummy = SplayNode(None, None)

    def size(self) -> int:
        return self._size

    def _get_root(self) -> Optional[BaseNode]:
        return self.root


    def _splay(self, key: Any, root: Optional[SplayNode]) -> Optional[SplayNode]:
        """
        Top-down splay operation. Brings node with key (or closest node) to the root.
        """
        if root is None:
            return None

        header = self._dummy
        header.left = None
        header.right = None
        left_tree_max = header
        right_tree_min = header

        t = root
        while True:
            self.comparisons += 1
            if key < t.key:
                if t.left is None:
                    break
                self.comparisons += 1
                if key < t.left.key:
                    # Zig-Zig: Rotate right
                    y = t.left
                    t.left = y.right
                    y.right = t
                    t = y
                    self.rotations += 1
                    self.structural_modifications += 1
                    if t.left is None:
                        break
                # Link right
                right_tree_min.left = t
                right_tree_min = t
                t = t.left
                self.structural_modifications += 1
            elif key > t.key:
                if t.right is None:
                    break
                self.comparisons += 1
                if key > t.right.key:
                    # Zag-Zag: Rotate left
                    y = t.right
                    t.right = y.left
                    y.left = t
                    t = y
                    self.rotations += 1
                    self.structural_modifications += 1
                    if t.right is None:
                        break
                # Link left
                left_tree_max.right = t
                left_tree_max = t
                t = t.right
                self.structural_modifications += 1
            else:
                break

        # Re-assemble
        left_tree_max.right = t.left
        right_tree_min.left = t.right
        t.left = header.right
        t.right = header.left
        return t

    def put(self, key: Any, value: Any) -> None:
        if self.root is None:
            self.root = SplayNode(key, value)
            self._size = 1
            return

        self.root = self._splay(key, self.root)
        if self.root.key == key:
            self.root.value = value
            return

        new_node = SplayNode(key, value)
        if key < self.root.key:
            new_node.left = self.root.left
            new_node.right = self.root
            self.root.left = None
        else:
            new_node.right = self.root.right
            new_node.left = self.root
            self.root.right = None

        self.root = new_node
        self._size += 1
        self.structural_modifications += 1

    def get(self, key: Any) -> Optional[Any]:
        if self.root is None:
            return None
        self.root = self._splay(key, self.root)
        if self.root.key == key:
            return self.root.value
        return None

    def contains(self, key: Any) -> bool:
        return self.get(key) is not None

    def delete(self, key: Any) -> bool:
        if self.root is None:
            return False

        self.root = self._splay(key, self.root)
        if self.root.key != key:
            return False

        # Node found at root
        if self.root.left is None:
            self.root = self.root.right
        else:
            right_sub = self.root.right
            self.root = self._splay(key, self.root.left)
            self.root.right = right_sub

        self._size -= 1
        self.structural_modifications += 1
        return True
