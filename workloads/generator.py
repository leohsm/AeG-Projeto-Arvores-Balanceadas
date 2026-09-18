import random
from typing import List, Tuple, Any, Optional
import numpy as np


class WorkloadGenerator:
    """
    Generates standardized workloads for benchmarking key-value stores.
    Workloads return a list of tuples: (operation, key, value)
    where operation in ('PUT', 'GET', 'DELETE').
    """
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.np_rng = np.random.default_rng(seed)

    def sequential_insert(self, n: int) -> List[Tuple[str, int, str]]:
        """
        Workload 6.a: Insercao Sequencial
        Inserts keys strictly in increasing order (0, 1, 2, ..., n-1).
        No get or delete during insertion.
        """
        return [("PUT", i, f"val_{i}") for i in range(n)]

    def random_insert(self, n: int) -> List[Tuple[str, int, str]]:
        """
        Workload 6.b: Insercao Aleatoria
        Shuffles the set of keys and inserts all once in random order.
        """
        keys = list(range(n))
        self.rng.shuffle(keys)
        return [("PUT", k, f"val_{k}") for k in keys]

    def mixed_oltp(self, n: int, initial_ratio: float = 0.2) -> Tuple[List[Tuple[str, int, str]], List[Tuple[str, int, str]]]:
        """
        Workload 6.c: Carga Mista (OLTP)
        50% put, 40% get, 10% delete. Keys chosen uniformly.
        Returns: (pre_populate_ops, workload_ops)
        """
        init_count = int(n * initial_ratio)
        init_keys = list(range(init_count))
        self.rng.shuffle(init_keys)
        pre_ops = [("PUT", k, f"val_{k}") for k in init_keys]

        active_keys = set(init_keys)
        next_new_key = init_count
        workload_ops: List[Tuple[str, int, str]] = []

        for _ in range(n):
            roll = self.rng.random()
            if roll < 0.50:  # 50% PUT
                # either update existing or insert new
                if active_keys and self.rng.random() < 0.4:
                    k = self.rng.choice(list(active_keys))
                else:
                    k = next_new_key
                    next_new_key += 1
                    active_keys.add(k)
                workload_ops.append(("PUT", k, f"val_{k}"))
            elif roll < 0.90:  # 40% GET
                if active_keys and self.rng.random() < 0.85:
                    k = self.rng.choice(list(active_keys))
                else:
                    k = self.rng.randint(0, next_new_key + 100)
                workload_ops.append(("GET", k, ""))
            else:  # 10% DELETE
                if active_keys:
                    k = self.rng.choice(list(active_keys))
                    active_keys.remove(k)
                    workload_ops.append(("DELETE", k, ""))
                else:
                    k = next_new_key
                    next_new_key += 1
                    active_keys.add(k)
                    workload_ops.append(("PUT", k, f"val_{k}"))

        return pre_ops, workload_ops

    def read_intensive(self, n: int, preload_ratio: float = 0.10) -> Tuple[List[Tuple[str, int, str]], List[Tuple[str, int, str]]]:
        """
        Workload 6.d: Leitura Intensiva
        Phase 1: Pre-populate ~10% of total volume
        Phase 2: 90% get, 5% put, 5% delete.
        """
        preload_count = max(10, int(n * preload_ratio))
        keys = list(range(preload_count))
        self.rng.shuffle(keys)
        pre_ops = [("PUT", k, f"val_{k}") for k in keys]

        active_keys = set(keys)
        next_new_key = preload_count
        workload_ops: List[Tuple[str, int, str]] = []

        for _ in range(n):
            roll = self.rng.random()
            if roll < 0.90:  # 90% GET
                if active_keys and self.rng.random() < 0.95:
                    k = self.rng.choice(list(active_keys))
                else:
                    k = self.rng.randint(0, next_new_key + 50)
                workload_ops.append(("GET", k, ""))
            elif roll < 0.95:  # 5% PUT
                k = next_new_key
                next_new_key += 1
                active_keys.add(k)
                workload_ops.append(("PUT", k, f"val_{k}"))
            else:  # 5% DELETE
                if active_keys:
                    k = self.rng.choice(list(active_keys))
                    active_keys.remove(k)
                    workload_ops.append(("DELETE", k, ""))
                else:
                    k = next_new_key
                    next_new_key += 1
                    active_keys.add(k)
                    workload_ops.append(("PUT", k, f"val_{k}"))

        return pre_ops, workload_ops

    def write_intensive(self, n: int, initial_ratio: float = 0.05) -> Tuple[List[Tuple[str, int, str]], List[Tuple[str, int, str]]]:
        """
        Workload 6.e: Escrita Intensiva
        70% put, 10% get, 20% delete. High ingestion volume.
        """
        init_count = max(10, int(n * initial_ratio))
        keys = list(range(init_count))
        self.rng.shuffle(keys)
        pre_ops = [("PUT", k, f"val_{k}") for k in keys]

        active_keys = set(keys)
        next_new_key = init_count
        workload_ops: List[Tuple[str, int, str]] = []

        for _ in range(n):
            roll = self.rng.random()
            if roll < 0.70:  # 70% PUT
                k = next_new_key
                next_new_key += 1
                active_keys.add(k)
                workload_ops.append(("PUT", k, f"val_{k}"))
            elif roll < 0.80:  # 10% GET
                if active_keys:
                    k = self.rng.choice(list(active_keys))
                else:
                    k = self.rng.randint(0, next_new_key + 20)
                workload_ops.append(("GET", k, ""))
            else:  # 20% DELETE
                if active_keys:
                    k = self.rng.choice(list(active_keys))
                    active_keys.remove(k)
                    workload_ops.append(("DELETE", k, ""))
                else:
                    k = next_new_key
                    next_new_key += 1
                    active_keys.add(k)
                    workload_ops.append(("PUT", k, f"val_{k}"))

        return pre_ops, workload_ops

    def zipfian_hotset(self, n: int, pool_size: int = 5000, s: float = 0.99) -> Tuple[List[Tuple[str, int, str]], List[Tuple[str, int, str]]]:
        """
        Workload 6.f: Zipfiano (zipfian_hotset)
        Skewed access distribution: Frequency ~ 1 / k^s.
        Pre-populates pool_size keys, then issues queries/updates where
        a tiny subset of hot keys receives most accesses.
        """
        preload_keys = list(range(pool_size))
        pre_ops = [("PUT", k, f"val_{k}") for k in preload_keys]

        ranks = np.arange(1, pool_size + 1, dtype=np.float64)
        weights = 1.0 / (ranks ** s)
        weights /= np.sum(weights)

        sampled_indices = self.np_rng.choice(pool_size, size=n, p=weights)

        workload_ops: List[Tuple[str, int, str]] = []
        for idx in sampled_indices:
            k = int(idx)
            roll = self.rng.random()
            if roll < 0.85:  # 85% hot GET
                workload_ops.append(("GET", k, ""))
            elif roll < 0.95:  # 10% hot PUT / update
                workload_ops.append(("PUT", k, f"updated_{k}"))
            else:  # 5% DELETE and re-insert
                workload_ops.append(("DELETE", k, ""))
                workload_ops.append(("PUT", k, f"reinserted_{k}"))

        return pre_ops, workload_ops
