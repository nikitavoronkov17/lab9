"""
Лабораторная работа № 9. Вариант 5.
Тип графа: Ц (цепочка), ориентированный.
Задача: сравнение рекурсивного и итеративного DFS;
доп. задание И5 — определение предела рекурсии и способов его обхода.

Запуск: python lab9_variant5.py
"""
import sys
import time
import threading


# ---------- Представления графа ----------

class ListDiGraph:
    """Ориентированный граф на списках смежности. Память Θ(n + m)."""

    def __init__(self, n):
        self.n = n
        self.adj = [[] for _ in range(n)]

    def add_edge(self, u, v):
        self.adj[u].append(v)

    def has_edge(self, u, v):
        return v in self.adj[u]

    def neighbors(self, v):
        return self.adj[v]


class MatrixDiGraph:
    """Ориентированный граф на матрице смежности. Память Θ(n²)."""

    def __init__(self, n):
        self.n = n
        self.matrix = [[0] * n for _ in range(n)]

    def add_edge(self, u, v):
        self.matrix[u][v] = 1

    def has_edge(self, u, v):
        return self.matrix[u][v] == 1

    def neighbors(self, v):
        row = self.matrix[v]
        return [u for u in range(self.n) if row[u]]


# ---------- Генератор графа ----------

def chain_digraph(cls, n):
    """Ориентированная цепочка 0 → 1 → … → n-1."""
    g = cls(n)
    for i in range(n - 1):
        g.add_edge(i, i + 1)
    return g


# ---------- Обходы ----------

def bfs(graph, start):
    """BFS. Возвращает (порядок, расстояния, предки)."""
    from collections import deque
    dist = [-1] * graph.n
    parent = [-1] * graph.n
    order = []
    dist[start] = 0
    q = deque([start])
    while q:
        v = q.popleft()
        order.append(v)
        for u in graph.neighbors(v):
            if dist[u] == -1:
                dist[u] = dist[v] + 1
                parent[u] = v
                q.append(u)
    return order, dist, parent


def dfs_iterative(graph, start):
    """Итеративный DFS на явном стеке. O(n + m)."""
    visited = [False] * graph.n
    order = []
    stack = [start]
    while stack:
        v = stack.pop()
        if visited[v]:
            continue
        visited[v] = True
        order.append(v)
        for u in reversed(graph.neighbors(v)):
            if not visited[u]:
                stack.append(u)
    return order


def dfs_recursive(graph, v, visited, order):
    """Рекурсивный DFS. Глубина рекурсии = длина пути."""
    visited[v] = True
    order.append(v)
    for u in graph.neighbors(v):
        if not visited[u]:
            dfs_recursive(graph, u, visited, order)


def dfs_recursive_wrapper(graph, start):
    visited = [False] * graph.n
    order = []
    dfs_recursive(graph, start, visited, order)
    return order


# ---------- Вспомогательные функции ----------

def deep_sizeof(obj):
    """Приблизительный расход памяти вложенной структуры, байт."""
    if isinstance(obj, list):
        return sys.getsizeof(obj) + sum(deep_sizeof(x) for x in obj)
    return sys.getsizeof(obj)


def run_recursive_safely(graph, start, stack_bytes=None):
    """
    Запуск рекурсивного DFS с опциональным увеличением C-стека
    через отдельный поток. Возвращает (время, статус).
    """
    status = {"ok": False, "err": None, "t": None}

    def runner():
        try:
            t0 = time.perf_counter()
            dfs_recursive_wrapper(graph, start)
            status["ok"] = True
            status["t"] = time.perf_counter() - t0
        except RecursionError:
            status["err"] = "RecursionError"

    if stack_bytes is None:
        runner()
    else:
        threading.stack_size(stack_bytes)
        th = threading.Thread(target=runner)
        th.start()
        th.join()
    return status["t"], (status["err"] or "OK")


# ---------- Основная программа ----------

if __name__ == "__main__":

    # --- 1. Малый тестовый граф ---
    print("=" * 60)
    print("Тестовый граф (6 вершин):")
    small = ListDiGraph(6)
    for u, v in [(0, 1), (1, 2), (2, 3), (3, 4), (1, 5)]:
        small.add_edge(u, v)
    print("  BFS:        ", [v + 1 for v in bfs(small, 0)[0]])
    print("  DFS итерат.:", [v + 1 for v in dfs_iterative(small, 0)])
    print("  DFS рекурс.:", [v + 1 for v in dfs_recursive_wrapper(small, 0)])

    # --- 2. Предел рекурсии при стандартном лимите ---
    print("\n" + "=" * 60)
    print(f"Ограничение рекурсии по умолчанию: {sys.getrecursionlimit()}")
    print(f"{'n':>10} | {'рекурсивный DFS':>20}")
    print("-" * 40)
    for n in [100, 500, 900, 990, 1000, 2000, 10_000, 100_000]:
        g = chain_digraph(ListDiGraph, n)
        _, status = run_recursive_safely(g, 0)
        print(f"{n:>10} | {status:>20}")

    # --- 3. Сравнение времени DFS при n = 1000, 10 000 ---
    print("\n" + "=" * 60)
    print("Сравнение времени обхода (списки смежности, лучшее из 3)")
    print(f"{'n':>8} | {'итеративный, мс':>18} | {'рекурсивный, мс':>18}")
    print("-" * 55)

    for n in [1000, 10_000]:
        g = chain_digraph(ListDiGraph, n)
        # итеративный
        times_it = []
        for _ in range(3):
            t0 = time.perf_counter()
            dfs_iterative(g, 0)
            times_it.append((time.perf_counter() - t0) * 1000)
        # рекурсивный с повышенным лимитом
        sys.setrecursionlimit(n + 200)
        times_rec = []
        for _ in range(3):
            t0 = time.perf_counter()
            dfs_recursive_wrapper(g, 0)
            times_rec.append((time.perf_counter() - t0) * 1000)
        sys.setrecursionlimit(1000)
        print(f"{n:>8} | {min(times_it):>18.2f} | {min(times_rec):>18.2f}")

    # --- 4. n = 100 000: рекурсивный падает, итеративный работает ---
    print("\n" + "=" * 60)
    print("n = 100 000:")
    g_big = chain_digraph(ListDiGraph, 100_000)

    t0 = time.perf_counter()
    dfs_iterative(g_big, 0)
    print(f"  итеративный DFS: {1000 * (time.perf_counter() - t0):.2f} мс — OK")

    # Пытаемся с повышенным лимитом и увеличенным C-стеком.
    # ВНИМАНИЕ: при неудаче возможен Segmentation fault —
    # это как раз демонстрирует предел рекурсивной реализации.
    sys.setrecursionlimit(200_000)
    t, status = run_recursive_safely(g_big, 0, stack_bytes=256 * 1024 * 1024)
    if status == "OK":
        print(f"  рекурсивный DFS (стек 256 МБ): {1000 * t:.2f} мс — OK")
    else:
        print(f"  рекурсивный DFS: {status} / переполнение C-стека")

    # --- 5. Память при n = 1000 ---
    print("\n" + "=" * 60)
    print("Расход памяти при n = 1000 (цепочка):")
    gm = chain_digraph(MatrixDiGraph, 1000)
    gl = chain_digraph(ListDiGraph, 1000)
    print(f"  матрица смежности : {deep_sizeof(gm.matrix) / 1024:>8.1f} КБ")
    print(f"  списки смежности  : {deep_sizeof(gl.adj) / 1024:>8.1f} КБ")