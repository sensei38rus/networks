import os
import glob
from collections import Counter

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "social-networks")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def load_graphs(data_dir: str) -> dict:
    """Загружает графы из файлов .edges."""
    return {
        os.path.splitext(os.path.basename(p))[0]: nx.read_edgelist(p, nodetype=int)
        for p in sorted(glob.glob(os.path.join(data_dir, "*.edges")))
    }


def analyze_graph(G: nx.Graph, name: str) -> dict:
    """Анализирует граф: распределение расстояний, статистика, график."""
    # Наибольшая связная компонента
    if nx.is_connected(G):
        G_main = G
    else:
        G_main = G.subgraph(max(nx.connected_components(G), key=len)).copy()

    # Распределение длин кратчайших путей
    distance_counts = Counter()
    for source, targets in nx.all_pairs_shortest_path_length(G_main):
        for target, dist in targets.items():
            if source < target:
                distance_counts[dist] += 1

    distance_counts = dict(sorted(distance_counts.items()))
    all_distances = np.array([d for d, c in distance_counts.items() for _ in range(c)])

    stats = {
        "name": name,
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "components": nx.number_connected_components(G),
        "main_size": G_main.number_of_nodes(),
        "mean": float(np.mean(all_distances)),
        "median": float(np.median(all_distances)),
        "mode": max(distance_counts, key=distance_counts.get),
        "max": int(np.max(all_distances)),
        "p90": float(np.percentile(all_distances, 90)),
        "total_pairs": len(all_distances),
        "pairs_within_6": sum(c for d, c in distance_counts.items() if d <= 6),
    }
    stats["percent_within_6"] = stats["pairs_within_6"] / stats["total_pairs"] * 100

    # График
    distances = list(distance_counts.keys())
    counts = list(distance_counts.values())

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(distances, counts, color="steelblue", edgecolor="navy", alpha=0.8)
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(counts) * 0.01,
                str(count), ha="center", va="bottom", fontsize=8)

    ax.set_xlabel("Длина кратчайшего пути", fontsize=12)
    ax.set_ylabel("Количество пар", fontsize=12)
    ax.set_title(f"Граф {name} | Среднее: {stats['mean']:.2f} | "
                 f"Медиана: {stats['median']:.1f} | Мода: {stats['mode']} | Макс: {stats['max']}",
                 fontsize=13)
    ax.set_xticks(distances)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"distribution_{name}.png"),
                dpi=150, bbox_inches="tight")
    plt.close()

    return stats


def print_summary_table(results: list):
    """Выводит сводную таблицу результатов."""
    print("\n" + "=" * 110)
    print("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    print("=" * 110)
    header = (f"{'Граф':<8} | {'Вершин':<8} | {'Рёбер':<8} | {'Компонент':<10} | "
              f"{'Ср.комп.':<9} | {'Среднее':<9} | {'Медиана':<8} | "
              f"{'Мода':<6} | {'Макс':<6} | {'P90':<6} | {'% пар ≤ 6':<10}")
    print(header)
    print("-" * 110)

    for r in results:
        print(f"{r['name']:<8} | {r['nodes']:<8} | {r['edges']:<8} | "
              f"{r['components']:<10} | {r['main_size']:<9} | "
              f"{r['mean']:<9.2f} | {r['median']:<8.1f} | "
              f"{r['mode']:<6} | {r['max']:<6} | {r['p90']:<6.1f} | "
              f"{r['percent_within_6']:<10.2f}%")

    print("=" * 110)


def interpret_results(results: list):
    """Краткая интерпретация результатов."""
    avg_mean = np.mean([r["mean"] for r in results])
    avg_pct = np.mean([r["percent_within_6"] for r in results])
    max_mean = max(results, key=lambda r: r["mean"])
    min_mean = min(results, key=lambda r: r["mean"])

    print("\n" + "=" * 110)
    print("ИНТЕРПРЕТАЦИЯ РЕЗУЛЬТАТОВ")
    print("=" * 110)

    theory_confirmed = avg_pct >= 90
    print(f"\n1. Теория шести рукопожатий: "
          f"{'ПОДТВЕРЖДАЕТСЯ' if theory_confirmed else 'НЕ ПОДТВЕРЖДАЕТСЯ'}")
    print(f"   Средний процент пар с расстоянием ≤ 6: {avg_pct:.2f}%")

    print(f"\n2. Средняя длина пути по всем графам: {avg_mean:.2f}")

    print(f"\n3. Влияние размера графа:")
    print(f"   Наименьшее среднее расстояние: граф {min_mean['name']} "
          f"({min_mean['nodes']} вершин) — {min_mean['mean']:.2f}")
    print(f"   Наибольшее среднее расстояние: граф {max_mean['name']} "
          f"({max_mean['nodes']} вершин) — {max_mean['mean']:.2f}")

    corr = np.corrcoef([r["nodes"] for r in results], [r["mean"] for r in results])[0, 1]
    trend = "увеличивается" if corr > 0.3 else "уменьшается" if corr < -0.3 else "практически не меняется"
    print(f"   Корреляция размера графа и средней длины пути: {corr:.3f} → при росте графа расстояние {trend}")

    print("=" * 110)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    graphs = load_graphs(DATA_DIR)

    results = [analyze_graph(G, name) for name, G in graphs.items()]

    print_summary_table(results)
    interpret_results(results)


if __name__ == "__main__":
    main()