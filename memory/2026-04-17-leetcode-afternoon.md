# LeetCode Practice - 2026-04-17 Afternoon

## Problem 1: Valid Parentheses (Medium) - 20
**Problem:** Determine if brackets are validly nested.

**Approach:** Stack with character matching
```python
def isValid(s):
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in mapping:
            top = stack.pop() if stack else '#'
            if mapping[char] != top:
                return False
        else:
            stack.append(char)
    
    return len(stack) == 0
```

**Time:** O(n), **Space:** O(n)

---

## Problem 2: Number of Islands (Medium) - 200
**Problem:** Count islands in a 2D grid.

**Approach:** DFS flood fill
```python
def numIslands(grid):
    if not grid:
        return 0
    
    def dfs(i, j):
        if i < 0 or j < 0 or i >= len(grid) or j >= len(grid[0]) or grid[i][j] == '0':
            return
        grid[i][j] = '0'
        dfs(i+1, j)
        dfs(i-1, j)
        dfs(i, j+1)
        dfs(i, j-1)
    
    count = 0
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == '1':
                count += 1
                dfs(i, j)
    
    return count
```

**Time:** O(m*n), **Space:** O(m*n)

---

## Problem 3: Clone Graph (Medium) - 133
**Problem:** Deep copy an undirected graph.

**Approach:** BFS with hash map
```python
def cloneGraph(node):
    if not node:
        return None
    
    visited = {node: Node(node.val)}
    queue = [node]
    
    while queue:
        current = queue.pop(0)
        for neighbor in current.neighbors:
            if neighbor not in visited:
                visited[neighbor] = Node(neighbor.val)
                queue.append(neighbor)
            visited[current].neighbors.append(visited[neighbor])
    
    return visited[node]
```

**Time:** O(V+E), **Space:** O(V)

---

## Key Insights

1. **Stack for matching** — Use stack to track opening brackets, pop on closing
2. **Flood fill** — Mark visited in-place to avoid double counting
3. **Graph cloning** — Always use visited hash map to handle cycles
4. **Queue for BFS** — Process level by level for graph traversal

**Topics:** Stack, DFS, BFS, Graph traversal