# LeetCode Practice - 2026-04-17 Evening

## Problem 1: Merge Intervals (Medium) - 56
**Problem:** Merge overlapping intervals.

**Approach:** Sort + single pass
```python
def merge(intervals):
    if not intervals:
        return []
    
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    
    for start, end in intervals[1:]:
        last_end = merged[-1][1]
        if start <= last_end:
            merged[-1][1] = max(last_end, end)
        else:
            merged.append([start, end])
    
    return merged
```

**Time:** O(n log n), **Space:** O(n)

---

## Problem 2: Insert Intervals (Medium) - 57
**Problem:** Insert a new interval into sorted non-overlapping intervals.

**Approach:** Find position, merge overlapping
```python
def insert(intervals, newInterval):
    result = []
    i = 0
    n = len(intervals)
    
    # Add all intervals before newInterval
    while i < n and intervals[i][1] < newInterval[0]:
        result.append(intervals[i])
        i += 1
    
    # Merge overlapping
    while i < n and intervals[i][0] <= newInterval[1]:
        newInterval[0] = min(newInterval[0], intervals[i][0])
        newInterval[1] = max(newInterval[1], intervals[i][1])
        i += 1
    result.append(newInterval)
    
    # Add remaining
    while i < n:
        result.append(intervals[i])
        i += 1
    
    return result
```

**Time:** O(n), **Space:** O(n)

---

## Problem 3: Maximum Subarray (Medium) - 53
**Problem:** Find the contiguous subarray with the largest sum.

**Approach:** Kadane's Algorithm
```python
def maxSubArray(nums):
    max_sum = nums[0]
    current_sum = nums[0]
    
    for num in nums[1:]:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    
    return max_sum
```

**Time:** O(n), **Space:** O(1)

---

## Key Insights

1. **Sort for intervals** — Sort by start time, then merge in single pass
2. **Three-phase insert** — Before, overlapping, after
3. **Kadane's algorithm** — Either extend previous sum or start fresh at current
4. **O(n log n) sorting** — Often the key to interval problems

**Topics:** Intervals, Sorting, Dynamic Programming, Greedy