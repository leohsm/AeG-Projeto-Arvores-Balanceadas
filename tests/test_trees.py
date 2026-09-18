import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import random
import unittest
from trees.splay_tree import SplayTree
from trees.bb_alpha_tree import WeightBalancedTree
from trees.aa_tree import AATree
from trees.scapegoat_tree import ScapegoatTree
from trees.zip_tree import ZipTree
from trees.wavl_tree import WAVLTree


class TestBalancedTrees(unittest.TestCase):
    def get_tree_classes(self):
        return [
            ("Splay", lambda: SplayTree()),
            ("BB[alpha]", lambda: WeightBalancedTree(alpha=0.29)),
            ("AA", lambda: AATree()),
            ("Scapegoat", lambda: ScapegoatTree(alpha=0.70)),
            ("Zip", lambda: ZipTree(seed=42)),
            ("WAVL", lambda: WAVLTree()),
        ]

    def test_basic_crud(self):
        for name, tree_ctor in self.get_tree_classes():
            with self.subTest(tree=name):
                t = tree_ctor()
                self.assertEqual(t.size(), 0)
                self.assertIsNone(t.get(10))
                self.assertFalse(t.contains(10))
                self.assertFalse(t.delete(10))

                # Insert elements
                t.put(10, "val10")
                t.put(5, "val5")
                t.put(15, "val15")
                t.put(3, "val3")
                t.put(7, "val7")

                self.assertEqual(t.size(), 5)
                self.assertEqual(t.get(10), "val10")
                self.assertEqual(t.get(5), "val5")
                self.assertEqual(t.get(15), "val15")
                self.assertEqual(t.get(3), "val3")
                self.assertEqual(t.get(7), "val7")
                self.assertIsNone(t.get(999))

                # In-order sorted property
                self.assertEqual(t.inorder_keys(), [3, 5, 7, 10, 15])

                # Update existing key
                t.put(10, "val10_updated")
                self.assertEqual(t.get(10), "val10_updated")
                self.assertEqual(t.size(), 5)

                # Delete leaf
                self.assertTrue(t.delete(3))
                self.assertIsNone(t.get(3))
                self.assertEqual(t.size(), 4)
                self.assertEqual(t.inorder_keys(), [5, 7, 10, 15])

                # Delete node with children
                self.assertTrue(t.delete(5))
                self.assertIsNone(t.get(5))
                self.assertEqual(t.size(), 3)
                self.assertEqual(t.inorder_keys(), [7, 10, 15])

                # Delete remaining
                self.assertTrue(t.delete(10))
                self.assertTrue(t.delete(7))
                self.assertTrue(t.delete(15))
                self.assertEqual(t.size(), 0)
                self.assertFalse(t.delete(10))

    def test_randomized_stress(self):
        rng = random.Random(12345)
        keys = list(range(2000))
        rng.shuffle(keys)

        for name, tree_ctor in self.get_tree_classes():
            with self.subTest(tree=name):
                t = tree_ctor()
                ref_dict = {}

                # Insert 1000 items
                for k in keys[:1000]:
                    v = f"val_{k}"
                    t.put(k, v)
                    ref_dict[k] = v

                self.assertEqual(t.size(), 1000)
                self.assertEqual(t.inorder_keys(), sorted(ref_dict.keys()))

                # Verify all get
                for k in list(ref_dict.keys())[:200]:
                    self.assertEqual(t.get(k), ref_dict[k])

                # Delete 500 items
                to_delete = keys[:500]
                for k in to_delete:
                    self.assertTrue(t.delete(k))
                    del ref_dict[k]

                self.assertEqual(t.size(), 500)
                self.assertEqual(t.inorder_keys(), sorted(ref_dict.keys()))

                # Verify remaining get
                for k in ref_dict:
                    self.assertEqual(t.get(k), ref_dict[k])

                # Verify deleted keys are gone
                for k in to_delete:
                    self.assertIsNone(t.get(k))
                    self.assertFalse(t.delete(k))

    def test_sequential_insertion(self):
        """Stress test with sequential numbers (0, 1, 2, ..., 1000) - worst case for naive BST."""
        for name, tree_ctor in self.get_tree_classes():
            with self.subTest(tree=name):
                t = tree_ctor()
                for i in range(1000):
                    t.put(i, i * 2)

                self.assertEqual(t.size(), 1000)
                self.assertEqual(t.inorder_keys(), list(range(1000)))

                # Balanced trees guarantee worst-case logarithmic height
                h = t.height()
                if name != "Splay":
                    self.assertLess(h, 45, f"{name} height is too large: {h}")
                else:
                    # Splay tree on strictly sequential insertions without reads creates a spine of length N
                    self.assertEqual(h, 1000)
                    # Once we access key 0, splay collapses the spine!
                    t.get(0)
                    self.assertLess(t.height(), 1000)

                # Test deletes in sequential order
                for i in range(500):
                    self.assertTrue(t.delete(i))
                self.assertEqual(t.size(), 500)
                self.assertEqual(t.inorder_keys(), list(range(500, 1000)))

    def test_tree_invariants(self):
        """Verify internal mathematical invariants for each balanced tree variant."""
        rng = random.Random(999)
        keys = list(range(500))
        rng.shuffle(keys)

        # 1. AA Tree invariants
        aa = AATree()
        for k in keys:
            aa.put(k, k)
        for k in keys[:150]:
            aa.delete(k)

        def _check_aa(node):
            if not node:
                return
            if node.left is None and node.right is None:
                self.assertEqual(node.level, 1, "AA Tree leaf must have level 1")
            if node.left:
                self.assertEqual(node.left.level, node.level - 1, "AA Tree left child must have level - 1")
                _check_aa(node.left)
            if node.right:
                self.assertIn(node.right.level, [node.level, node.level - 1], "AA Tree right child level")
                if node.right.right:
                    self.assertLess(node.right.right.level, node.level, "AA Tree no consecutive horizontal links")
                _check_aa(node.right)
        _check_aa(aa.root)

        # 2. WAVL Tree invariants
        wavl = WAVLTree()
        for k in keys:
            wavl.put(k, k)
        for k in keys[:150]:
            wavl.delete(k)

        def _check_wavl(node):
            if not node:
                return
            diff_l = wavl._diff(node, node.left)
            diff_r = wavl._diff(node, node.right)
            self.assertIn(diff_l, [1, 2], f"WAVL left rank diff must be 1 or 2, got {diff_l}")
            self.assertIn(diff_r, [1, 2], f"WAVL right rank diff must be 1 or 2, got {diff_r}")
            if node.left is None and node.right is None:
                self.assertEqual(node.rank, 0, "WAVL leaf must have rank 0")
            _check_wavl(node.left)
            _check_wavl(node.right)
        _check_wavl(wavl.root)

        # 3. Zip Tree invariants
        zip_t = ZipTree(seed=123)
        for k in keys:
            zip_t.put(k, k)
        for k in keys[:150]:
            zip_t.delete(k)

        def _check_zip(node):
            if not node:
                return
            if node.left:
                # Left child priority
                self.assertTrue(node.left.rank < node.rank or (node.left.rank == node.rank and node.left.key < node.key))
                _check_zip(node.left)
            if node.right:
                # Right child priority
                self.assertTrue(node.right.rank <= node.rank)
                _check_zip(node.right)
        _check_zip(zip_t.root)

        # 4. BB[alpha] weight consistency
        bb = WeightBalancedTree(alpha=0.29)
        for k in keys:
            bb.put(k, k)
        for k in keys[:150]:
            bb.delete(k)

        def _check_bb(node):
            if not node:
                return 1
            wl = _check_bb(node.left)
            wr = _check_bb(node.right)
            expected = wl + wr
            self.assertEqual(node.weight, expected)
            return expected
        _check_bb(bb.root)


if __name__ == "__main__":
    unittest.main()
