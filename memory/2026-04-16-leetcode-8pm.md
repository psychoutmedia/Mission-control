# LeetCode Practice — 2026-04-16 Night Cap

**Time:** 8:13 PM
**Topic:** Trie (Medium) — Quick Session

---

## Problem 1: Implement Trie (LC 208)

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
    
    def search(self, word):
        node = self._search_prefix(word)
        return node is not None and node.is_end
    
    def startsWith(self, prefix):
        return self._search_prefix(prefix) is not None
    
    def _search_prefix(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node
```

**Key insight:** Prefix tree. Each node has children dict + is_end flag.
Search = walk path + check is_end. StartsWith = walk path only.

**Complexity:** O(m) for all operations where m = word/prefix length

---

## Problem 2: Longest Common Prefix (LC 14)

```python
def longestCommonPrefix(strs):
    if not strs:
        return ""
    
    # Find minimum length string
    min_len = min(len(s) for s in strs)
    if min_len == 0:
        return ""
    
    # Binary search on prefix length
    low, high = 0, min_len
    while low < high:
        mid = (low + high + 1) // 2
        prefix = strs[0][:mid]
        if all(s.startswith(prefix) for s in strs):
            low = mid
        else:
            high = mid - 1
    
    return strs[0][:low]
```

**Alternative (simpler):**

```python
def longestCommonPrefix(strs):
    if not strs:
        return ""
    
    prefix = strs[0]
    for s in strs[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix
```

**Key insight:** Horizontal scanning — compare character by character across all strings.

**Complexity:** O(n × m) time worst case (n strings, avg length m), O(1) space

---

## Day Final Summary — 2026-04-16

| Session | Time | Topic | Problems |
|---------|------|-------|----------|
| 1 | 6:03 AM | Graphs (Union-Find, TopoSort, Multi-source DFS) | 3 |
| 2 | 12:02 PM | Dynamic Programming (LIS, Coin Change, LCS) | 3 |
| 3 | 1:02 PM | Binary Search (Find Min, Rotated II, Median) | 3 |
| 4 | 3:13 PM | Backtracking (Combinations, Permutations II, Word Search) | 3 |
| 5 | 5:13 PM | Stack/Monotonic (Daily Temps, Car Fleet, Min Swaps) | 3 |
| 6 | 6:13 PM | Greedy/Intervals (Non-overlap, Meeting Rooms, Gas Station) | 3 |
| 7 | 7:13 PM | Matrix (Set Zeroes, Spiral Matrix, Rotate Image) | 3 |
| 8 | 8:13 PM | Trie (Implement Trie, Longest Common Prefix) | 2 |

**Total: 8 sessions, 23 problems.**

Git: Clean. Helios-1 spec: Done. Portfolio README: Polished.

💤 Day complete.
