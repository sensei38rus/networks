import sys
from itertools import combinations

def has_4_cycle(n, edges):
    adj = [set() for _ in range(n + 1)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    for a, b in combinations(range(1, n + 1), 2):
        if len(adj[a] & adj[b]) >= 2:
            return True
    return False

def main():
    input_file = "square_graph_dataset.txt"
    output_file = "output.txt"

    with open(input_file, "r", encoding="utf-8") as f:
        data = f.read().split()

    idx = 0
    t = int(data[idx]); idx += 1
    results = []

    for _ in range(t):
        n = int(data[idx]); idx += 1
        m = int(data[idx]); idx += 1

        edges = []
        for _ in range(m):
            u = int(data[idx]); idx += 1
            v = int(data[idx]); idx += 1
            edges.append((u, v))

        results.append("1" if has_4_cycle(n, edges) else "-1")

    result_str = " ".join(results)
    print(result_str)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result_str + "\n")

if __name__ == "__main__":
    main()