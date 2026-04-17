# LeetCode Practice - 2026-04-17 Morning

## Problem 1: Number of Islands (Medium)
**Problem:** Given a 2D grid of '1's (land) and '0's (water), count the number of islands.

**Approach:** BFS/DFS flood fill
```python
def numIslands(grid):
    if not grid:
        return 0
    
    rows, cols = len(grid), len(grid[0])
    islands = 0
    
    def dfs(r, c):
        if r < 0 or c < 0 or r >= rows or c >= cols or grid[r][c] == '0':
            return
        grid[r][c] = '0'  # Mark visited
        dfs(r+1, c)
        dfs(r-1, c)
        dfs(r, c+1)
        dfs(r, c-1)
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                islands += 1
                dfs(r, c)
    
    return islands
```

**Time:** O(m*n), **Space:** O(m*n) for recursion stack

---

## Problem 2: Clone Graph (Medium)
**Problem:** Return a deep copy of an undirected graph.

**Approach:** BFS with visited hash map
```python
def cloneGraph(self, node):
    if not node:
        return None
    
    # Map old node -> new node
    clone = {node: Node(node.val, [])}
    queue = [node]
    
    while queue:
        current = queue.pop(0)
        for neighbor in current.neighbors:
            if neighbor not in clone:
                clone[neighbor] = Node(neighbor.val, [])
                queue.append(neighbor)
            clone[current].neighbors.append(clone[neighbor])
    
    return clone[node]
```

**Time:** O(V+E), **Space:** O(V)

---

## Problem 3: Longest Consecutive Sequence (Medium)
**Problem:** Find the length of the longest consecutive sequence in an unsorted array.

**Approach:** Set + greedy expansion (avoid sorting)
```python
def longestConsecutive(nums):
    num_set = set(nums)
    longest = 0
    
    for num in num_set:
        # Only start from the beginning of a sequence
        if num - 1 not in num_set:
            current = num
            streak = 1
            while current + 1 in num_set:
                current += 1
                streak += 1
            longest = max(longest, streak)
    
    return longest
```

**Time:** O(n), **Space:** O(n)

---

## Key Insights

1. **Flood fill pattern** — For island/region problems, mark visited in-place
2. **Graph cloning** — Keep hash map of old→new to handle cycles
3. **Consecutive sequences** — Use set, only expand from sequence starts (num-1 not in set)
4. **BFS vs DFS** — BFS for level-order, shortest path; DFS for exploring all paths

**Total problems solved today:** 3 medium
**Cumulative streak:** Graph problems are now solid