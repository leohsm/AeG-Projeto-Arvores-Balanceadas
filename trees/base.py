from abc import ABC, abstractmethod
from collections import deque
from typing import Any, Optional, Tuple, List
import sys

# Increase recursion limit for deep tree operations if ever needed
sys.setrecursionlimit(200000)


class BaseNode:
    """Base class for binary search tree nodes."""
    def __init__(self, key: Any, value: Any):
        self.key = key
        self.value = value
        self.left: Optional['BaseNode'] = None
        self.right: Optional['BaseNode'] = None

    def __repr__(self) -> str:
        return f"Node({self.key}: {self.value})"


class KeyValueStore(ABC):
    """
    Abstract Base Class for an In-Memory Key-Value Store based on Balanced Trees.
    Defines common operations: put, get, delete, size, height, and rebalance metrics.
    """
    def __init__(self, name: str):
        self.name = name
        self.rotations: int = 0
        self.structural_modifications: int = 0
        self.comparisons: int = 0

    @abstractmethod
    def put(self, key: Any, value: Any) -> None:
        """Insert or update a key-value pair."""
        pass

    @abstractmethod
    def get(self, key: Any) -> Optional[Any]:
        """Retrieve the value associated with key, or None if not found."""
        pass

    @abstractmethod
    def delete(self, key: Any) -> bool:
        """Remove the key-value pair. Returns True if deleted, False if not found."""
        pass

    @abstractmethod
    def contains(self, key: Any) -> bool:
        """Check if key exists in the store."""
        pass

    @abstractmethod
    def size(self) -> int:
        """Return the total number of keys stored."""
        pass

    def height(self) -> int:
        """Calculate maximum tree height iteratively (0 if empty)."""
        root = self._get_root()
        if root is None:
            return 0
        max_h = 0
        stack = [(root, 1)]
        while stack:
            node, d = stack.pop()
            if d > max_h:
                max_h = d
            if node.right:
                stack.append((node.right, d + 1))
            if node.left:
                stack.append((node.left, d + 1))
        return max_h

    def reset_metrics(self) -> None:
        """Reset internal performance counters."""
        self.rotations = 0
        self.structural_modifications = 0
        self.comparisons = 0

    def get_metrics(self) -> dict:
        """Return dictionary of structural metrics."""
        return {
            "rotations": self.rotations,
            "structural_modifications": self.structural_modifications,
            "comparisons": self.comparisons,
            "height": self.height(),
            "size": self.size(),
            "average_depth": round(self.average_depth(), 2),
        }

    def average_depth(self) -> float:
        """Calculate average node depth for the tree iteratively."""
        root = self._get_root()
        n = self.size()
        if n == 0 or root is None:
            return 0.0

        total_depth = 0
        queue = deque([(root, 1)])
        while queue:
            node, depth = queue.popleft()
            total_depth += depth
            if node.left:
                queue.append((node.left, depth + 1))
            if node.right:
                queue.append((node.right, depth + 1))

        return total_depth / n

    @abstractmethod
    def _get_root(self) -> Optional[BaseNode]:
        """Return tree root node for inspection/traversals."""
        pass

    def inorder_keys(self) -> List[Any]:
        """Return list of keys in sorted order iteratively."""
        keys = []
        stack = []
        curr = self._get_root()
        while curr is not None or stack:
            while curr is not None:
                stack.append(curr)
                curr = curr.left
            curr = stack.pop()
            keys.append(curr.key)
            curr = curr.right
        return keys
