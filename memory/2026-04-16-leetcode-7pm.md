# LeetCode Practice — 2026-04-16 Night

**Time:** 7:13 PM
**Topic:** Matrix & Simulation (Medium)
**Session goal:** 3 medium problems

---

## Problem 1: Set Matrix Zeroes (LC 73)

```python
def setZeroes(matrix):
    rows, cols = len(matrix), len(matrix[0])
    first_row_zero = any(matrix[0][j] == 0 for j in range(cols))
    first_col_zero = any(matrix[i][0] == 0 for i in range(rows))
    
    # Mark zeros in first row and column
    for i in range(1, rows):
        for j in range(1, cols):
            if matrix[i][j] == 0:
                matrix[i][0] = 0
                matrix[0][j] = 0
    
    # Zero out based on marks
    for i in range(1, rows):
        if matrix[i][0] == 0:
            for j in range(1, cols):
                matrix[i][j] = 0
    
    for j in range(1, cols):
        if matrix[0][j] == 0:
            for i in range(1, rows):
                matrix[i][j] = 0
    
    # Zero out first row/col if needed
    if first_row_zero:
        for j in range(cols):
            matrix[0][j] = 0
    if first_col_zero:
        for i in range(rows):
            matrix[i][0] = 0
```

**Key insight:** O(1) space using first row/col as markers.
Track if first row/col needs zeroing, then use them as markers.

**Complexity:** O(m × n) time, O(1) space

---

## Problem 2: Spiral Matrix (LC 54)

```python
def spiralOrder(matrix):
    result = []
    rows, cols = len(matrix), len(matrix[0])
    top, bottom, left, right = 0, rows - 1, 0, cols - 1
    
    while top <= bottom and left <= right:
        # Top row
        for j in range(left, right + 1):
            result.append(matrix[top][j])
        top += 1
        
        # Right column
        for i in range(top, bottom + 1):
            result.append(matrix[i][right])
        right -= 1
        
        # Bottom row
        if top <= bottom:
            for j in range(right, left - 1, -1):
                result.append(matrix[bottom][j])
            bottom -= 1
        
        # Left column
        if left <= right:
            for i in range(bottom, top - 1, -1):
                result.append(matrix[i][left])
            left += 1
    
    return result
```

**Key insight:** Bounded simulation with 4 pointers. Classic boundary tracking.
Be careful to check bounds after shrinking top/left.

**Complexity:** O(m × n) time, O(1) space

---

## Problem 3: Rotate Image (LC 48)

```python
def rotate(matrix):
    """
    In-place rotation: Transpose then reverse each row.
    Or: Reverse rows, then transpose.
    """
    n = len(matrix)
    
    # Transpose
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    
    # Reverse each row
    for i in range(n):
        matrix[i].reverse()
```

**Key insight:** 90° clockwise = transpose + reverse rows (or reverse cols + transpose).
Math: (i,j) → (j,n-1-i) via transpose then row-reverse.

**Complexity:** O(m × n) time, O(1) space

---

## Summary

| Problem | Technique | Key Insight |
|---------|-----------|-------------|
| Set Matrix Zeroes (LC 73) | In-place markers | Use first row/col as O(1) storage |
| Spiral Matrix (LC 54) | Bounded simulation | 4 pointers, boundary checks |
| Rotate Image (LC 48) | Transpose + reverse | (i,j) → (j,n-1-i) |

**Why this matters for LLM Engineering:**
- Matrix traversal = attention pattern visualization
- In-place operations = memory efficiency in CUDA kernels
- Simulation patterns = token grid operations in vision transformers

---

## Day Summary — 2026-04-16

| Session | Time | Topic | Problems |
|---------|------|-------|----------|
| 1 | 6:03 AM | Graphs (Union-Find, TopoSort, Multi-source DFS) | 3 |
| 2 | 12:02 PM | Dynamic Programming (LIS, Coin Change, LCS) | 3 |
| 3 | 1:02 PM | Binary Search (Find Min, Rotated II, Median) | 3 |
| 4 | 3:13 PM | Backtracking (Combinations, Permutations II, Word Search) | 3 |
| 5 | 5:13 PM | Stack/Monotonic (Daily Temps, Car Fleet, Min Swaps) | 3 |
| 6 | 6:13 PM | Greedy/Intervals (Non-overlap, Meeting Rooms, Gas Station) | 3 |
| 7 | 7:13 PM | Matrix (Set Zeroes, Spiral, Rotate) | 3 |

**Total: 7 sessions, 21 problems solved.**

Other work:
- Helios-1 Technical Specification (full spec)
- Git history cleaned (git-filter-repo)
- cot_streaming_agent README polished (9KB)
- Queue updated and pushed to origin

**Patterns covered:** Graphs, DP, Binary Search, Backtracking, Stack, Greedy, Matrix — all major LeetCode medium patterns.

**Next:** Trie problems, Linked Lists, or advanced DP (DP on trees).
