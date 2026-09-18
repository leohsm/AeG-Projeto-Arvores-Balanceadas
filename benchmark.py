import os
import sys
import time
import json
import csv
import math
from typing import List, Dict, Any, Callable

# Ensure local imports work seamlessly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from trees import SplayTree, WeightBalancedTree, AATree, ScapegoatTree, ZipTree, WAVLTree, KeyValueStore
from workloads import WorkloadGenerator


def create_tree_factory() -> Dict[str, Callable[[], KeyValueStore]]:
    return {
        "Splay Tree": lambda: SplayTree(),
        "BB[alpha] (0.29)": lambda: WeightBalancedTree(alpha=0.29),
        "AA Tree": lambda: AATree(),
        "Scapegoat (0.70)": lambda: ScapegoatTree(alpha=0.70),
        "Zip Tree": lambda: ZipTree(seed=12345),
        "WAVL Tree": lambda: WAVLTree(),
    }


def execute_ops(tree: KeyValueStore, ops: List[tuple]) -> None:
    for op, k, v in ops:
        if op == "PUT":
            tree.put(k, v)
        elif op == "GET":
            tree.get(k)
        elif op == "DELETE":
            tree.delete(k)


def run_single_benchmark(tree_name: str, tree_ctor: Callable[[], KeyValueStore],
                         workload_name: str, pre_ops: List[tuple],
                         workload_ops: List[tuple]) -> Dict[str, Any]:
    tree = tree_ctor()

    # Pre-population if required
    if pre_ops:
        execute_ops(tree, pre_ops)

    tree.reset_metrics()

    start_ns = time.perf_counter_ns()
    execute_ops(tree, workload_ops)
    end_ns = time.perf_counter_ns()

    elapsed_ms = (end_ns - start_ns) / 1_000_000.0
    num_ops = len(workload_ops)
    throughput = (num_ops / (elapsed_ms / 1000.0)) if elapsed_ms > 0 else 0.0

    metrics = tree.get_metrics()
    tree_size = metrics["size"]
    h = metrics["height"]
    min_h = math.ceil(math.log2(tree_size + 1)) if tree_size > 0 else 0

    return {
        "tree": tree_name,
        "workload": workload_name,
        "ops_count": num_ops,
        "time_ms": round(elapsed_ms, 2),
        "throughput_ops_sec": round(throughput, 1),
        "height": h,
        "min_possible_height": min_h,
        "height_ratio": round(h / max(1, min_h), 2),
        "average_depth": metrics["average_depth"],
        "rotations": metrics["rotations"],
        "structural_mods": metrics["structural_modifications"],
        "comparisons": metrics["comparisons"],
        "final_size": tree_size,
    }


def run_benchmark_suite(n_ops: int = 25000, runs: int = 3, output_dir: str = "results") -> List[Dict[str, Any]]:
    os.makedirs(output_dir, exist_ok=True)
    tree_factories = create_tree_factory()

    print(f"================================================================")
    print(f" BENCHMARK ÁRVORES BALANCEADAS - BANCO CHAVE-VALOR EM MEMÓRIA")
    print(f" Configuração: {n_ops:,} operações por workload | {runs} repetições")
    print(f"================================================================")

    # Prepare workloads once to ensure identical inputs across all trees
    gen = WorkloadGenerator(seed=42)

    seq_ops = gen.sequential_insert(n_ops)
    rand_ops = gen.random_insert(n_ops)
    m_pre, m_ops = gen.mixed_oltp(n_ops)
    r_pre, r_ops = gen.read_intensive(n_ops)
    w_pre, w_ops = gen.write_intensive(n_ops)
    z_pre, z_ops = gen.zipfian_hotset(n_ops, pool_size=min(10000, n_ops // 2))

    workloads = [
        ("Insercao Sequencial", [], seq_ops),
        ("Insercao Aleatoria", [], rand_ops),
        ("Carga Mista (OLTP)", m_pre, m_ops),
        ("Leitura Intensiva", r_pre, r_ops),
        ("Escrita Intensiva", w_pre, w_ops),
        ("Zipfiano (Hotset)", z_pre, z_ops),
    ]

    all_results: List[Dict[str, Any]] = []

    for w_name, pre_ops, main_ops in workloads:
        print(f"\n>>> Executando Workload: {w_name} ({len(main_ops):,} ops) ...")
        print(f"{'Árvore':<20} | {'Tempo (ms)':<10} | {'Ops/seg':<12} | {'Altura':<8} | {'Rot/Mod':<10} | {'Comp/op':<8}")
        print("-" * 75)

        for t_name, ctor in tree_factories.items():
            run_times = []
            run_throughputs = []
            last_res = {}

            for r in range(runs):
                res = run_single_benchmark(t_name, ctor, w_name, pre_ops, main_ops)
                run_times.append(res["time_ms"])
                run_throughputs.append(res["throughput_ops_sec"])
                last_res = res

            avg_time = round(sum(run_times) / len(run_times), 2)
            avg_throughput = round(sum(run_throughputs) / len(run_throughputs), 1)
            comp_per_op = round(last_res["comparisons"] / max(1, last_res["ops_count"]), 2)
            rot_mods = f"{last_res['rotations']}/{last_res['structural_mods']}"

            print(f"{t_name:<20} | {avg_time:<10} | {avg_throughput:<12} | {last_res['height']:<8} | {rot_mods:<10} | {comp_per_op:<8}")

            aggregated_entry = {
                **last_res,
                "time_ms": avg_time,
                "throughput_ops_sec": avg_throughput,
                "runs": runs,
            }
            all_results.append(aggregated_entry)

    # Save to JSON
    json_path = os.path.join(output_dir, "benchmark_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    # Save to CSV
    csv_path = os.path.join(output_dir, "benchmark_results.csv")
    fieldnames = list(all_results[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    print(f"\n================================================================")
    print(f" Benchmark finalizado com sucesso!")
    print(f" Resultados salvos em:")
    print(f" - JSON: {json_path}")
    print(f" - CSV:  {csv_path}")
    print(f"================================================================")

    return all_results


if __name__ == "__main__":
    n = 25000
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    run_benchmark_suite(n_ops=n, runs=3)
