# LeetCode Practice — 2026-04-14 Night

## Session: Trees & Graphs

---

### 1. Binary Tree Level Order Traversal (102) — Medium

**Problem:** Given the root of a binary tree, return the level order traversal of its nodes' values (left to right, level by level).

**Approach:** BFS using a queue. Process nodes level by level, track when we transition between levels.

```python
from collections import deque

def levelOrder(root: Optional[TreeNode]) -> list[list[int]]:
    if not root:
        return []
    
    result = []
    queue = deque([root])
    
    while queue:
        level_size = len(queue)  # Number of nodes at current level
        current_level = []
        
        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        result.append(current_level)
    
    return result
```

**Complexity:** O(n) time, O(w) space where w = max width of tree  
**Key insight:** `len(queue)` at start of each level = number of nodes at that level.

**DFS alternative:**
```python
def levelOrder_dfs(root):
    result = []
    
    def dfs(node, depth):
        if not node:
            return
        if depth >= len(result):
            result.append([])
        result[depth].append(node.val)
        dfs(node.left, depth + 1)
        dfs(node.right, depth + 1)
    
    dfs(root, 0)
    return result
```

---

### 2. Clone Graph (133) — Medium

**Problem:** Return a deep copy (clone) of an undirected graph. Each node contains an integer label and a list of neighbors.

**Approach:** BFS/DFS with a hash map to track already-cloned nodes (avoids infinite loops on cycles).

```python
from collections import deque

def cloneGraph(node: 'Node') -> 'Node':
    if not node:
        return None
    
    # Map original node -> cloned node
    clones = {node: Node(node.val, [])}
    queue = deque([node])
    
    while queue:
        current = queue.popleft()
        
        for neighbor in current.neighbors:
            if neighbor not in clones:
                # Clone neighbor and add to queue
                clones[neighbor] = Node(neighbor.val, [])
                queue.append(neighbor)
            
            # Add cloned neighbor to cloned current node
            clones[current].neighbors.append(clones[neighbor])
    
    return clones[node]
```

**Complexity:** O(n) time, O(n) space  
**Key insight:** The hash map serves dual purpose — tracks cloned nodes AND prevents revisiting cycles.

**DFS (recursive) version:**
```python
def cloneGraph_dfs(node, visited={}):
    if not node:
        return None
    
    if node in visited:
        return visited[node]
    
    cloned = Node(node.val, [])
    visited[node] = cloned
    
    for neighbor in node.neighbors:
        cloned.neighbors.append(cloneGraph_dfs(neighbor, visited))
    
    return cloned
```

---

### 3. Longest Consecutive Sequence (128) — Hard

**Problem:** Given an unsorted array of integers, find the length of the longest consecutive sequence (elements that form consecutive integers like [1, 2, 3, 4]). Must be O(n) time.

**Approach:** Convert to set for O(1) lookup, then for each num, check if it's the start of a sequence (num-1 not in set), then count consecutive upward.

```python
def longestConsecutive(nums: list[int]) -> int:
    if not nums:
        return 0
    
    # Convert to set for O(1) lookup
    num_set = set(nums)
    longest = 0
    
    for num in num_set:
        # Only start counting if this is the start of a sequence
        if num - 1 not in num_set:
            current_num = num
            current_streak = 1
            
            # Count upward
            while current_num + 1 in num_set:
                current_num += 1
                current_streak += 1
            
            longest = max(longest, current_streak)
    
    return longest
```

**Complexity:** O(n) time, O(n) space  
**Key insight:** The `num - 1 not in num_set` check ensures we only start counting at sequence starts — avoids O(n²) from starting at every element.

**Alternative: Sort then scan** (O(n log n)):
```python
def longestConsecutive_sorted(nums):
    if not nums:
        return 0
    
    nums.sort()
    longest = 1
    current = 1
    
    for i in range(1, len(nums)):
        if nums[i] == nums[i-1] + 1:
            current += 1
        elif nums[i] != nums[i-1]:
            current = 1
        longest = max(longest, current)
    
    return longest
```

---

## Summary

| Problem | Difficulty | Time | Space | Pattern |
|---------|-----------|------|-------|---------|
| Binary Tree Level Order | Medium | O(n) | O(w) | BFS / Queue |
| Clone Graph | Medium | O(n) | O(n) | BFS + Hash Map |
| Longest Consecutive Sequence | Hard | O(n) | O(n) | Set + Sequence Detection |

**Total:** 3 problems — BFS, graph cloning, consecutive sequence

**Patterns reinforced:**
- BFS with queue for level-order traversal
- Hash map for cycle detection and node cloning
- Set for O(1) membership checking
- Sequence detection: check for sequence start before counting

**Next session:** Consider Trie problems, or back to dynamic programming (House Robber, Decode Ways)
