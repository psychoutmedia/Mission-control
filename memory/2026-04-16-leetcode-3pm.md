# LeetCode Practice — 2026-04-16 Afternoon

**Time:** 3:13 PM
**Topic:** Recursion & Backtracking (Medium)
**Session goal:** 3 medium problems

---

## Problem 1: Combinations (LC 77)

```python
def combine(n, k):
    result = []
    
    def backtrack(start, path):
        if len(path) == k:
            result.append(path[:])
            return
        # Pruning: if not enough elements left, skip
        for i in range(start, n + 1):
            path.append(i)
            backtrack(i + 1, path)
            path.pop()
    
    backtrack(1, [])
    return result
```

**Key insight:** Classic combination generator. Use `i+1` to avoid duplicates (combinations, not permutations).
Prune with `n - i >= k - len(path)`.

**Complexity:** O(C(n,k) × k) time, O(k) space (call stack + path)

---

## Problem 2: Permutations II (LC 47)

```python
def permuteUnique(nums):
    nums.sort()
    result = []
    used = [False] * len(nums)
    
    def backtrack(path):
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            # Skip duplicates: if same num used already at this level, skip
            if used[i] or (i > 0 and nums[i] == nums[i-1] and not used[i-1]):
                continue
            used[i] = True
            path.append(nums[i])
            backtrack(path)
            path.pop()
            used[i] = False
    
    backtrack([])
    return result
```

**Key insight:** Sort first, then skip duplicates with `used[i-1] == False` check.
The duplicate skip condition ensures we only start with the first occurrence of each duplicate.

**Complexity:** O(n! × n) time worst case, O(n) space

---

## Problem 3: Word Search II (LC 212) — Trie + DFS

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.word = None

class Solution:
    def findWords(self, board, words):
        root = TrieNode()
        
        # Build Trie
        for word in words:
            node = root
            for char in word:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            node.word = word
        
        result = []
        rows, cols = len(board), len(board[0])
        
        def dfs(r, c, node):
            char = board[r][c]
            if char not in node.children:
                return
            next_node = node.children[char]
            if next_node.word:
                result.append(next_node.word)
                next_node.word = None  # Avoid duplicates
            board[r][c] = '#'  # Mark visited
            for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    dfs(nr, nc, next_node)
            board[r][c] = char  # Restore
        
        for r in range(rows):
            for c in range(cols):
                dfs(r, c, root)
        
        return result
```

**Key insight:** Build Trie first (O(total chars)), then DFS from each cell.
Mark visited with in-board value change, not separate visited set.

**Complexity:** O(m × n × 4^L) worst case for DFS, but Trie pruning helps significantly

---

## Summary

| Problem | Key Technique | Pruning Trick |
|---------|---------------|---------------|
| Combinations (LC 77) | i+1 to avoid duplicates | Not enough elements left |
| Permutations II (LC 47) | Sort + used[] array | Skip duplicate starts |
| Word Search II (LC 212) | Trie + DFS | Mark visited in-place |

**Why this matters for LLM Engineering:**
- Backtracking = beam search in transformers
- Trie = prefix tree for autocomplete, RAG retrieval
- Permutations = token ordering/arrangement problems

**Next session:** String matching (KMP, Rabin-Karp) or Union-Find advanced problems.
