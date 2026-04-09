# LeetCode Practice — Evening Session (PM2)
**Date:** 2026-04-09  
**Focus:** 3 Medium problems covering different algorithmic patterns

---

## 1. Course Schedule (LeetCode 207)

### Problem
Determine if you can finish all courses given prerequisites. Return `True` if no cycle exists in the prerequisite graph.

### Solution — Kahn's Algorithm (BFS Topological Sort)

```python
from collections import defaultdict, deque

def canFinish(numCourses: int, prerequisites: list[list[int]]) -> bool:
    """
    Determine if you can finish all courses given prerequisites.
    Uses Kahn's algorithm (BFS topological sort).
    A cycle in the graph means courses cannot be completed.
    """
    if not prerequisites:
        return True

    # Build adjacency list and in-degree count
    graph = defaultdict(list)
    in_degree = [0] * numCourses

    for dest, src in prerequisites:
        graph[src].append(dest)
        in_degree[dest] += 1

    # Start with courses that have no prerequisites (in-degree 0)
    queue = deque([i for i in range(numCourses) if in_degree[i] == 0])
    finished = 0

    while queue:
        course = queue.popleft()
        finished += 1
        for neighbor in graph[course]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # If we finished all courses, no cycle existed
    return finished == numCourses
```

### Key Insight
- Build a directed graph from prerequisites
- Use in-degree (number of incoming edges) to detect nodes with no blockers
- Process nodes in BFS order; if we can't process all nodes → cycle exists

### Complexity
- **Time:** O(V + E) — visit each vertex and edge once
- **Space:** O(V + E) — adjacency list and in-degree array

### Test Cases Verified
| Input | Expected | Result |
|-------|----------|--------|
| `canFinish(2, [[1,0]])` | `True` | ✅ |
| `canFinish(2, [[1,0],[0,1]])` | `False` (cycle) | ✅ |
| `canFinish(5, [[1,4],[2,4],[3,1],[3,2]])` | `True` | ✅ |
| `canFinish(0, [])` | `True` | ✅ |

---

## 2. Longest Consecutive Sequence (LeetCode 128)

### Problem
Find the length of the longest consecutive sequence in an unsorted array (e.g., `[100, 4, 200, 1, 3, 2]` → `4` for `[1,2,3,4]`).

### Solution — Hash Set

```python
def longestConsecutive(nums: list[int]) -> int:
    """
    Find the length of the longest consecutive sequence.
    Uses a hash set for O(1) lookup.
    Key insight: only start counting from the beginning of a sequence
    (when num-1 is NOT in the set) to avoid redundant work.
    """
    if not nums:
        return 0

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

### Key Insight
- Convert to a set for O(1) membership checks
- Only start counting from sequence **starters** (where `num-1` is NOT in set)
- This avoids O(n²) by skipping already-counted sequence elements

### Complexity
- **Time:** O(n) — each element is visited at most twice (once as potential starter, once during streak counting)
- **Space:** O(n) — hash set storage

### Test Cases Verified
| Input | Expected | Result |
|-------|----------|--------|
| `[100,4,200,1,3,2]` | `4` | ✅ |
| `[0,3,7,2,5,8,4,6,0,1]` | `9` | ✅ |
| `[]` | `0` | ✅ |
| `[1]` | `1` | ✅ |
| `[1,2,0,1]` | `3` | ✅ |

---

## 3. Find Minimum in Rotated Sorted Array (LeetCode 153)

### Problem
A sorted array was rotated by some pivot. Find the minimum element. (e.g., `[3,4,5,1,2]` → `1`)

### Solution — Binary Search

```python
def findMin(nums: list[int]) -> int:
    """
    Find the minimum element in a rotated sorted array.
    Uses binary search with smart pivot logic.
    The minimum is the only element where both neighbors are larger,
    OR the first element if not rotated, OR the pivot point.
    """
    left, right = 0, len(nums) - 1

    # If not rotated, return first element
    if nums[left] <= nums[right]:
        return nums[left]

    while left < right:
        mid = (left + right) // 2
        # If mid is greater than mid+1, mid+1 is the minimum
        if nums[mid] > nums[mid + 1]:
            return nums[mid + 1]
        # If mid-1 is greater than mid, mid is the minimum
        if mid > left and nums[mid - 1] > nums[mid]:
            return nums[mid]
        # Decide which half to search
        if nums[mid] >= nums[left]:
            # Minimum is in the right half
            left = mid + 1
        else:
            # Minimum is in the left half
            right = mid - 1

    return nums[left]
```

### Key Insight
- The array is sorted and rotated, so there's a pivot point
- Binary search narrows the search space by half each iteration
- The minimum is where the "rotation" happens — the point where the sequence wraps

### Complexity
- **Time:** O(log n) — binary search halves the search space each iteration
- **Space:** O(1) — only pointer variables used

### Test Cases Verified
| Input | Expected | Result |
|-------|----------|--------|
| `[3,4,5,1,2]` | `1` | ✅ |
| `[4,5,6,7,0,1,2]` | `0` | ✅ |
| `[11,13,15,17]` | `11` (not rotated) | ✅ |
| `[2,1]` | `1` | ✅ |
| `[1]` | `1` | ✅ |

---

## Summary

| Problem | Pattern | Time | Space |
|---------|---------|------|-------|
| Course Schedule | Topological Sort / Cycle Detection | O(V + E) | O(V + E) |
| Longest Consecutive Sequence | Hash Set | O(n) | O(n) |
| Find Min in Rotated Array | Binary Search | O(log n) | O(1) |

All solutions verified with test cases. ✅
