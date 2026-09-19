import os
import json
import matplotlib.pyplot as plt
import numpy as np

# Set matplotlib styling for publication quality
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300


def load_results(json_path: str = "results/benchmark_results.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_all_plots(results_path: str = "results/benchmark_results.json", output_dir: str = "plots"):
    os.makedirs(output_dir, exist_ok=True)
    data = load_results(results_path)

    # Unique trees and workloads in order
    trees = ["Splay Tree", "BB[alpha] (0.29)", "AA Tree", "Scapegoat (0.70)", "Zip Tree", "WAVL Tree"]
    workloads = [
        "Insercao Sequencial",
        "Insercao Aleatoria",
        "Carga Mista (OLTP)",
        "Leitura Intensiva",
        "Escrita Intensiva",
        "Zipfiano (Hotset)",
    ]

    colors = {
        "Splay Tree": "#E63946",
        "BB[alpha] (0.29)": "#457B9D",
        "AA Tree": "#2A9D8F",
        "Scapegoat (0.70)": "#E76F51",
        "Zip Tree": "#F4A261",
        "WAVL Tree": "#1D3557",
    }

    # Helper mapping (workload, tree) -> entry
    lookup = {}
    for entry in data:
        lookup[(entry["workload"], entry["tree"])] = entry

    # -------------------------------------------------------------
    # 1. THROUGHPUT COMPARISON PER WORKLOAD
    # -------------------------------------------------------------
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()

    for idx, w_name in enumerate(workloads):
        ax = axes[idx]
        throughputs = [lookup.get((w_name, t), {}).get("throughput_ops_sec", 0) / 1000.0 for t in trees]
        bar_colors = [colors[t] for t in trees]

        bars = ax.bar(trees, throughputs, color=bar_colors, edgecolor="black", linewidth=0.8, width=0.6)
        ax.set_title(f"{w_name}", fontsize=13, fontweight="bold", pad=10)
        ax.set_ylabel("Throughput (milhares de ops/s)", fontsize=10)
        ax.tick_params(axis='x', rotation=35, labelsize=9)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"{height:.1f}k",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, fontweight="bold")

    plt.suptitle("Throughput por Workload (Operações / Segundo)", fontsize=16, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plot1_path = os.path.join(output_dir, "throughput_comparison.png")
    plt.savefig(plot1_path, dpi=300)
    plt.close()
    print(f"Saved: {plot1_path}")

    # -------------------------------------------------------------
    # 2. EXECUTION TIME COMPARISON (LOG SCALE)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.arange(len(workloads))
    width = 0.13

    for i, t in enumerate(trees):
        times = [lookup.get((w, t), {}).get("time_ms", 0) for w in workloads]
        offset = (i - len(trees) / 2) * width + width / 2
        ax.bar(x + offset, times, width, label=t, color=colors[t], edgecolor="black", linewidth=0.6)

    ax.set_yscale('log')
    ax.set_xticks(x)
    ax.set_xticklabels(workloads, fontsize=11, fontweight="bold")
    ax.set_ylabel("Tempo de Execução Médio (ms) [Escala Logarítmica]", fontsize=12, fontweight="bold")
    ax.set_title("Tempo de Execução por Workload e Estrutura", fontsize=15, fontweight="bold", pad=15)
    ax.legend(title="Árvore Balanceada", fontsize=10, loc="upper right")
    ax.grid(True, which="both", ls="--", alpha=0.5)

    plt.tight_layout()
    plot2_path = os.path.join(output_dir, "execution_time_comparison.png")
    plt.savefig(plot2_path, dpi=300)
    plt.close()
    print(f"Saved: {plot2_path}")

    # -------------------------------------------------------------
    # 3. TREE HEIGHT vs OPTIMAL HEIGHT
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.arange(len(workloads))
    width = 0.13

    for i, t in enumerate(trees):
        heights = []
        for w in workloads:
            h = lookup.get((w, t), {}).get("height", 0)
            if t == "Splay Tree" and w == "Insercao Sequencial":
                heights.append(58)  # visually capped
            else:
                heights.append(h)
        offset = (i - len(trees) / 2) * width + width / 2
        bars = ax.bar(x + offset, heights, width, label=t, color=colors[t], edgecolor="black", linewidth=0.6)

        if t == "Splay Tree":
            for idx_w, w in enumerate(workloads):
                if w == "Insercao Sequencial":
                    actual_height = lookup[(w, t)]["height"]
                    ax.annotate(f"{actual_height:,}\n(espinha)".replace(",", "."),
                                xy=(x[idx_w] + offset, 58),
                                xytext=(0, 4), textcoords="offset points",
                                ha='center', va='bottom', fontsize=8, fontweight='bold', color='#E63946')

    # Plot theoretical optimal height line
    opt_heights = [lookup.get((w, "WAVL Tree"), {}).get("min_possible_height", 0) for w in workloads]
    ax.plot(x, opt_heights, 'k--', marker='o', linewidth=2, label="Altura Mínima Teórica ceil(log2(N+1))")

    ax.set_ylim(0, 75)
    ax.set_xticks(x)
    ax.set_xticklabels(workloads, fontsize=11, fontweight="bold")
    ax.set_ylabel("Altura da Árvore ao Final do Workload", fontsize=12, fontweight="bold")
    ax.set_title("Eficiência de Balanceamento: Altura Final das Árvores", fontsize=15, fontweight="bold", pad=15)
    ax.legend(fontsize=10, loc="upper right")
    ax.grid(True, ls="--", alpha=0.6)

    plt.tight_layout()
    plot3_path = os.path.join(output_dir, "tree_height_comparison.png")
    plt.savefig(plot3_path, dpi=300)
    plt.close()
    print(f"Saved: {plot3_path}")

    # -------------------------------------------------------------
    # 4. REBALANCING OVERHEAD: ROTATIONS & MODIFICATIONS
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Rotations (Mixed OLTP and Random Insert)
    selected_w = ["Insercao Aleatoria", "Carga Mista (OLTP)"]
    for idx, w_name in enumerate(selected_w):
        ax = axes[idx]
        rots = [lookup.get((w_name, t), {}).get("rotations", 0) for t in trees]
        mods = [lookup.get((w_name, t), {}).get("structural_mods", 0) for t in trees]

        x_pos = np.arange(len(trees))
        ax.bar(x_pos - 0.2, rots, 0.4, label="Rotações", color="#457B9D", edgecolor="black")
        ax.bar(x_pos + 0.2, mods, 0.4, label="Modificações Estruturais", color="#E63946", edgecolor="black")

        ax.set_xticks(x_pos)
        ax.set_xticklabels(trees, rotation=35, fontsize=9)
        ax.set_ylabel("Quantidade de Operações de Ajuste", fontsize=10)
        ax.set_title(f"Sobrecarga de Rebalanceamento: {w_name}", fontsize=12, fontweight="bold")
        ax.legend(fontsize=9)
        ax.grid(True, ls="--", alpha=0.6)

    plt.suptitle("Custo Estrutural de Rebalanceamento", fontsize=15, fontweight="bold")
    plt.tight_layout()
    plot4_path = os.path.join(output_dir, "rebalance_overhead.png")
    plt.savefig(plot4_path, dpi=300)
    plt.close()
    print(f"Saved: {plot4_path}")

    # -------------------------------------------------------------
    # 5. COMPARISONS PER OPERATION
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(workloads))
    width = 0.13

    for i, t in enumerate(trees):
        comp_per_op = []
        for w in workloads:
            entry = lookup.get((w, t), {})
            ops = max(1, entry.get("ops_count", 1))
            comps = entry.get("comparisons", 0)
            comp_per_op.append(comps / ops)

        offset = (i - len(trees) / 2) * width + width / 2
        ax.bar(x + offset, comp_per_op, width, label=t, color=colors[t], edgecolor="black", linewidth=0.6)

    ax.set_xticks(x)
    ax.set_xticklabels(workloads, fontsize=11, fontweight="bold")
    ax.set_ylabel("Comparações de Chaves por Operação", fontsize=12, fontweight="bold")
    ax.set_title("Custo Algorítmico: Média de Comparações por Operação", fontsize=15, fontweight="bold", pad=15)
    ax.legend(title="Árvore", fontsize=10, loc="upper right")
    ax.grid(True, ls="--", alpha=0.6)

    plt.tight_layout()
    plot5_path = os.path.join(output_dir, "comparisons_per_op.png")
    plt.savefig(plot5_path, dpi=300)
    plt.close()
    print(f"Saved: {plot5_path}")

    # -------------------------------------------------------------
    # 6. ZIPFIAN LOCALITY & HOTSET DEPTH ANALYSIS
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5.5))
    tree_short = ["Splay", "BB[alpha]", "AA", "Scapegoat", "Zip", "WAVL"]
    zipf_entries = [lookup.get(("Zipfiano (Hotset)", tree), {}) for tree in trees]
    hot_depths = [entry.get("hot_average_depth", 0) for entry in zipf_entries]
    cold_depths = [entry.get("cold_average_depth", 0) for entry in zipf_entries]

    x = np.arange(len(tree_short))
    width = 0.35

    rects1 = ax.bar(x - width/2, hot_depths, width, label='Chaves Quentes (Top 10 Zipf)', color='#E63946', edgecolor='black')
    rects2 = ax.bar(x + width/2, cold_depths, width, label='Chaves Frias (Rank > 500)', color='#457B9D', edgecolor='black')

    ax.set_ylabel('Profundidade Média do Nó', fontsize=11, fontweight='bold')
    ax.set_title('Efeito de Localidade sob Carga Zipfiana: Profundidade Quente vs Fria', fontsize=13, fontweight='bold', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(tree_short, fontsize=10, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, axis='y', ls='--', alpha=0.6)

    for bar in rects1:
        h = bar.get_height()
        ax.annotate(f'{h:.1f}', xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 2),
                    textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold')
    for bar in rects2:
        h = bar.get_height()
        ax.annotate(f'{h:.1f}', xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 2),
                    textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold')

    plt.tight_layout()
    plot6_path = os.path.join(output_dir, "zipfian_locality.png")
    plt.savefig(plot6_path, dpi=300)
    plt.close()
    print(f"Saved: {plot6_path}")

    print("All plots generated successfully!")


if __name__ == "__main__":
    generate_all_plots()
