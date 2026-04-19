# LeetCode Practice — 2026-04-19 Noon

**3 Medium Graph Problems** — All solved ✅

---

## 695. Max Area of Island (Medium)
**Problem:** Find the max area of any island. Island = connected 1s (4-directional).

**Approach:** DFS/BFS. For each unvisited island cell, explore the whole connected component and track the area. Keep global max.

```python
def maxAreaOfIsland(grid):
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    max_area = 0
    
    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols:
            return 0
        if visited[r][c] or grid[r][c] == 0:
            return 0
        visited[r][c] = True
        return 1 + dfs(r+1, c) + dfs(r-1, c) + dfs(r, c+1) + dfs(r, c-1)
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and not visited[r][c]:
                area = dfs(r, c)
                max_area = max(max_area, area)
    return max_area
```

**Key insight:** Use visited set or modify grid in-place. DFS recursively explores 4 directions.

**Time:** O(m*n) **Space:** O(m*n)

**Test:** grid1 → 6 ✅ | grid2 (no island) → 0 ✅

---

## 1466. Reorder Routes (Medium)
**Problem:** Make all paths lead from node 0. Min number of edge direction changes.

**Approach:** BFS from node 0. Build adjacency list with direction cost:
- `(neighbor, 1)` = outgoing edge (needs reorder)
- `(neighbor, 0)` = incoming edge (already correct)

```python
def minReorder(n, connections):
    from collections import defaultdict, deque
    graph = defaultdict(list)
    for u, v in connections:
        graph[u].append((v, 1))   # need to reorder
        graph[v].append((u, 0))   # already correct
    
    visited = [False] * n
    queue = deque([0])
    visited[0] = True
    reorders = 0
    
    while queue:
        node = queue.popleft()
        for neighbor, cost in graph[node]:
            if not visited[neighbor]:
                visited[neighbor] = True
                reorders += cost
                queue.append(neighbor)
    return reorders
```

**Key insight:** Track edge "cost" in adjacency list — 1 if it's an original outgoing edge, 0 if incoming. BFS sums the costs.

**Time:** O(n) **Space:** O(n)

**Test:** n=6, conns=[[0,1],[1,3],[2,3],[4,0],[4,5]] → 3 ✅

---

## 1971. Find if Path Exists (Medium)
**Problem:** Determine if a valid path exists between source and destination in an undirected graph.

**Approach:** BFS/DFS/Union-Find. Simple reachability check.

```python
def validPath(n, edges, source, destination):
    if source == destination:
        return True
    
    from collections import defaultdict, deque
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    
    visited = [False] * n
    queue = deque([source])
    visited[source] = True
    
    while queue:
        node = queue.popleft()
        if node == destination:
            return True
        for neighbor in graph[node]:
            if not visited[neighbor]:
                visited[neighbor] = True
                queue.append(neighbor)
    return False
```

**Key insight:** Early return if source == destination. BFS explores level by level.

**Time:** O(n) **Space:** O(n)

**Test:** n=3, edges=[[0,1],[1,2],[2,0]], src=0, dst=2 → True ✅
**Test:** n=6, edges=[[0,1],[0,2],[3,5],[5,4],[4,3]], src=0, dst=5 → False ✅

---

## Patterns Learned

1. **Island problems** → DFS/BFS with visited tracking, count connected components
2. **Graph direction problems** → Encode direction cost in adjacency list, BFS sums costs
3. **Path existence** → BFS/DFS/Union-Find, early termination when target found
4. **Visited array** → Essential to avoid infinite loops in graphs with cycles
