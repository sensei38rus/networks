from collections import defaultdict, deque
import sys

sys.setrecursionlimit(10000)


def load_graph(filename):
    """Загружает неориентированный граф из файла SNAP.
    Каждое ребро в файле записано дважды (u v и v u) — дедуплицируем."""
    graph = defaultdict(set)
    edges_set = set()

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) != 2:
                continue
            u, v = int(parts[0]), int(parts[1])
            if u == v:
                continue
            graph[u].add(v)
            graph[v].add(u)
            edges_set.add((u, v) if u < v else (v, u))

    return graph, edges_set


def has_alternative_path(graph, start, end, max_depth=6):
    """
    BFS: существует ли путь start -> end длиной >= 2,
    не идущий напрямую по ребру (start, end).
    max_depth ограничивает глубину обхода.
    """
    visited = {start}
    queue = deque()

    for neighbor in graph[start]:
        if neighbor != end:
            visited.add(neighbor)
            queue.append((neighbor, 2))

    while queue:
        node, length = queue.popleft()
        if node == end:
            return True
        if length >= max_depth:
            continue
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, length + 1))

    return False


def find_weakly_connected_pairs(graph, edges, max_depth=6, log_every=500):
    """Ищет все слабо связанные пары (u, v)."""
    result = []
    edges_list = list(edges)
    total = len(edges_list)

    for i, (u, v) in enumerate(edges_list, 1):
        if has_alternative_path(graph, u, v, max_depth=max_depth):
            result.append((u, v, len(graph[u]), len(graph[v])))
        if i % log_every == 0:
            print(f"  обработано рёбер: {i}/{total}, найдено пар: {len(result)}")

    return result


def write_results(output_file, graph, edges, pairs, stats):
    """Записывает результаты в файл."""
    with open(output_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("РЕЗУЛЬТАТЫ ПОИСКА СЛАБО СВЯЗАННЫХ ВЕРШИН\n")
        f.write("=" * 70 + "\n\n")

        # --- Статистика графа ---
        f.write("СТАТИСТИКА ГРАФА\n")
        f.write("-" * 70 + "\n")
        f.write(f"Исходный файл:               {stats['input_file']}\n")
        f.write(f"Узлов в графе:               {len(graph)}\n")
        f.write(f"Уникальных рёбер (неориент.): {len(edges)}\n")
        f.write(f"Максимальная глубина обхода: {stats['max_depth']}\n")
        f.write(f"Условие '>= 10 рёбер':       {'ВЫПОЛНЕНО' if len(edges) >= 10 else 'НЕ ВЫПОЛНЕНО'}\n")
        f.write("\n")

        # --- Итоги поиска ---
        f.write("ИТОГИ ПОИСКА\n")
        f.write("-" * 70 + "\n")
        f.write(f"Всего слабо связанных пар:   {len(pairs)}\n")
        f.write(f"Доля от всех рёбер:          {len(pairs)/len(edges)*100:.2f}%\n")
        f.write("\n")

        # --- Список пар ---
        f.write("СЛАБО СВЯЗАННЫЕ ПАРЫ\n")
        f.write("-" * 70 + "\n")
        f.write(f"{'№':>6}  {'Вершина U':>10}  {'Вершина V':>10}  "
                f"{'Степень U':>10}  {'Степень V':>10}\n")
        f.write("-" * 70 + "\n")

        for idx, (u, v, du, dv) in enumerate(pairs, 1):
            f.write(f"{idx:>6}  {u:>10}  {v:>10}  {du:>10}  {dv:>10}\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write("КОНЕЦ ОТЧЁТА\n")
        f.write("=" * 70 + "\n")


def main():
    input_file = "as19980428.txt"
    output_file = "output.txt"
    max_depth = 6

    # 1. Загрузка
    print(f"Загрузка графа из '{input_file}'...")
    graph, edges = load_graph(input_file)
    print(f"Узлов: {len(graph)}")
    print(f"Уникальных рёбер: {len(edges)}")

    if len(edges) < 10:
        print("В графе меньше 10 рёбер — условие задачи не выполнено.")
        # всё равно пишем отчёт
        stats = {
            'input_file': input_file,
            'max_depth': max_depth,
        }
        write_results(output_file, graph, edges, [], stats)
        print(f"Отчёт записан в '{output_file}' (пар не найдено).")
        return

    # 2. Поиск
    print(f"\nПоиск слабо связанных пар (глубина <= {max_depth})...")
    pairs = find_weakly_connected_pairs(graph, edges, max_depth=max_depth)
    print(f"Найдено пар: {len(pairs)}")

    # 3. Запись в файл
    stats = {
        'input_file': input_file,
        'max_depth': max_depth,
    }
    write_results(output_file, graph, edges, pairs, stats)
    print(f"\nРезультат записан в '{output_file}'")


if __name__ == "__main__":
    main()