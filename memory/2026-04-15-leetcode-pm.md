# LeetCode Practice — April 15, 2026 — Afternoon Session

## Problem 1: Subsets (Medium)
**Category:** Backtracking

```python
def subsets(nums):
    result = []
    
    def backtrack(start, path):
        result.append(path[:])  # Add copy of current path
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()
    
    backtrack(0, [])
    return result

# Example: [1,2,3] → [[], [1], [1,2], [1,2,3], [1,3], [1,3,2], [2], [2,3], [2,3,1], [3]]
# Time: O(n * 2^n) — each of 2^n subsets takes O(n) to copy
# Space: O(n) for recursion stack + O(2^n) for result storage
```

**Key insight:** Classic backtracking — at each position, you can either include or exclude the current element. Build up all possible combinations.

---

## Problem 2: Non-overlapping Intervals (Medium)
**Category:** Intervals / Greedy

```python
def erase_overlap_intervals(intervals):
    if not intervals:
        return 0
    
    # Sort by end coordinate
    intervals.sort(key=lambda x: x[1])
    count = 0
    end = intervals[0][1]
    
    for i in range(1, len(intervals)):
        if intervals[i][0] < end:  # Overlap detected
            count += 1
        else:
            end = intervals[i][1]  # No overlap, update end
    
    return count

# Example: [[1,2], [2,3], [3,4], [1,3]] → 1 (remove [1,3])
# Time: O(n log n) for sorting
# Space: O(1) extra (or O(n) for sorted copy)
```

**Key insight:** Greedy — always remove the interval that ends latest while overlapping. Sort by end time, greedily keep intervals that end earliest.

---

## Problem 3: Daily Temperatures (Medium)
**Category:** Stack / Monotonic Stack

```python
def daily_temperatures(temperatures):
    n = len(temperatures)
    result = [0] * n
    stack = []  # Store indices
    
    for i, temp in enumerate(temperatures):
        # Check if current temp is warmer than temps in stack
        while stack and temperatures[stack[-1]] < temp:
            prev_index = stack.pop()
            result[prev_index] = i - prev_index
        stack.append(i)
    
    return result

# Example: [73, 74, 75, 71, 69, 72, 76, 73] → [1, 1, 4, 2, 1, 1, 0, 0]
# Time: O(n) — each element pushed/popped at most once
# Space: O(n) for stack
```

**Key insight:** Monotonic decreasing stack — keeps track of temperatures we haven't found a warmer day for yet. When we find a warmer temp, we resolve all smaller temps in the stack.

---

## Summary
| Problem | Category | Pattern |
|---------|----------|---------|
| Subsets | Backtracking | Decision tree, include/exclude |
| Non-overlapping Intervals | Greedy | Sort by end, greedy removal |
| Daily Temperatures | Monotonic Stack | Decreasing stack, resolve on warmer |

**Total problems solved this session:** 3 medium
