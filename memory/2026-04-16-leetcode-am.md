# LeetCode Practice — 2026-04-16 Morning

**Time:** 6:03 AM
**Topic:** Graphs & DFS/BFS (Medium)
**Session goal:** 3 medium problems

---

## Problem 1: Number of Connected Components in an Undirected Graph (LC 323)

```python
def countComponents(n, edges):
    # Union-Find approach
    parent = list(range(n))
    rank = [0] * n
    
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        px, py = find(x), find(y)
        if px == py:
            return False
        if rank[px] < rank[py]:
            px, py = py, px
        parent[py] = px
        if rank[px] == rank[py]:
            rank[px] += 1
        return True
    
    for a, b in edges:
        union(a, b)
    
    return len(set(find(i) for i in range(n)))
```

**Key insight:** Union-Find (Disjoint Set) — O(V+E), path compression + union by rank makes it near-linear.

**Complexity:** O(V + E) time, O(V) space

---

## Problem 2: Course Schedule II (LC 210) — Topological Sort

```python
from collections import defaultdict, deque

def findOrder(numCourses, prerequisites):
    graph = defaultdict(list)
    in_degree = [0] * numCourses
    
    for dst, src in prerequisites:
        graph[src].append(dst)
        in_degree[dst] += 1
    
    queue = deque([i for i in range(numCourses) if in_degree[i] == 0])
    result = []
    
    while queue:
        node = queue.popleft()
        result.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return result if len(result) == numCourses else []
```

**Key insight:** Kahn's algorithm (BFS topological sort). Also solvable with DFS/backtracking.

**Complexity:** O(V + E) time, O(V + E) space

---

## Problem 3: Pacific Atlantic Water Flow (LC 417)

```python
def pacificAtlantic(heights):
    if not heights:
        return []
    
    rows, cols = len(heights), len(heights[0])
    pacific = [[False] * cols for _ in range(rows)]
    atlantic = [[False] * cols for _ in range(rows)]
    
    def dfs(r, c, visited, prev_height):
        if (r < 0 or c < 0 or r == rows or c == cols or
            visited[r][c] or heights[r][c] < prev_height):
            return
        visited[r][c] = True
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            dfs(r+dr, c+dc, visited, heights[r][c])
    
    # Left and top edges → Pacific
    for c in range(cols):
        dfs(0, c, pacific, heights[0][c])
    for r in range(rows):
        dfs(r, 0, pacific, heights[r][0])
    
    # Right and bottom edges → Atlantic
    for c in range(cols):
        dfs(rows-1, c, atlantic, heights[rows-1][c])
    for r in range(rows):
        dfs(r, cols-1, atlantic, heights[r][cols-1])
    
    return [[r, c] for r in range(rows) for c in range(cols)
            if pacific[r][c] and atlantic[r][c]]
```

**Key insight:** Multi-source BFS/DFS from both oceans simultaneously. Cells reachable from both = valid.

**Complexity:** O(R*C) time, O(R*C) space

---

## Summary

| Problem | Approach | Key Concept |
|---------|----------|-------------|
| Connected Components | Union-Find | DSU with path compression |
| Course Schedule II | Topological Sort (Kahn's) | BFS + in-degree |
| Pacific Atlantic | Multi-source DFS | Reverse flow from edges |

**Graph patterns:** Union-Find, Topological Sort, BFS/DFS from boundaries — all foundational for LLM engineering (dependency graphs, attention masks, etc.)

**Next session:** Consider topological sort variants, or move to dynamic programming.
