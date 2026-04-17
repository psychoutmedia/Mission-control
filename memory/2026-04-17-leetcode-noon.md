# LeetCode Practice - 2026-04-17 Late Morning

## Problem 1: Course Schedule (Medium) - 207
**Problem:** Determine if you can finish all courses given prerequisites.

**Approach:** Topological Sort (Kahn's Algorithm)
```python
def canFinish(numCourses, prerequisites):
    # Build adjacency list and calculate in-degrees
    graph = [[] for _ in range(numCourses)]
    in_degree = [0] * numCourses
    
    for dest, src in prerequisites:
        graph[src].append(dest)
        in_degree[dest] += 1
    
    # Start with courses that have no prerequisites
    queue = [i for i in range(numCourses) if in_degree[i] == 0]
    count = 0
    
    while queue:
        course = queue.pop(0)
        count += 1
        for neighbor in graph[course]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return count == numCourses
```

**Time:** O(V+E), **Space:** O(V+E)

---

## Problem 2: Course Schedule II (Medium) - 210
**Problem:** Return the order of courses to finish given prerequisites.

**Approach:** Topological Sort with order tracking
```python
def findOrder(numCourses, prerequisites):
    graph = [[] for _ in range(numCourses)]
    in_degree = [0] * numCourses
    
    for dest, src in prerequisites:
        graph[src].append(dest)
        in_degree[dest] += 1
    
    queue = [i for i in range(numCourses) if in_degree[i] == 0]
    result = []
    
    while queue:
        course = queue.pop(0)
        result.append(course)
        for neighbor in graph[course]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return result if len(result) == numCourses else []
```

**Time:** O(V+E), **Space:** O(V+E)

---

## Problem 3: Pacific Atlantic Water Flow (Medium) - 417
**Problem:** Find cells that can flow to both Pacific and Atlantic oceans.

**Approach:** BFS from edges + reverse thinking
```python
def pacificAtlantic(heights):
    if not heights:
        return []
    
    rows, cols = len(heights), len(heights[0])
    pacific = [[False] * cols for _ in range(rows)]
    atlantic = [[False] * cols for _ in range(rows)]
    
    def bfs(queue, visited):
        while queue:
            r, c = queue.pop(0)
            visited[r][c] = True
            for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                    if heights[nr][nc] >= heights[r][c]:
                        queue.append((nr, nc))
    
    # Start from Pacific (top + left edges) and Atlantic (bottom + right edges)
    pac_queue = [(0, i) for i in range(cols)] + [(i, 0) for i in range(1, rows)]
    atl_queue = [(rows-1, i) for i in range(cols)] + [(i, cols-1) for i in range(rows-1)]
    
    bfs(pac_queue, pacific)
    bfs(atl_queue, atlantic)
    
    # Find cells that can reach both
    result = []
    for r in range(rows):
        for c in range(cols):
            if pacific[r][c] and atlantic[r][c]:
                result.append([r, c])
    
    return result
```

**Time:** O(m*n), **Space:** O(m*n)

---

## Key Insights

1. **Topological Sort** — Detect cycles in directed graph (prerequisites). Use in-degree to find starting nodes.
2. **Course Schedule pattern** — Build graph from prerequisites, BFS/DFS from nodes with in-degree 0.
3. **Reverse BFS** — For water flow, start from ocean edges and work backwards.
4. **Multiple boundary BFS** — For Pacific/Atlantic, start BFS from two different edge sets.

**Total problems solved:** 3 medium
**Topics covered:** Graphs, Topological Sort, DFS/BFS