# LeetCode Practice - 2026-04-17 Late Afternoon

## Problem 1: Merge Intervals (Medium) - 56
**Problem:** Merge overlapping intervals.

**Approach:** Sort + single pass merge
```python
def merge(intervals):
    if not intervals:
        return []
    
    # Sort by start time
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

**Time:** O(n log n), **Space:** O(1) extra (or O(n) for output)

---

## Problem 2: Container With Most Water (Medium) - 11
**Problem:** Find max area between two vertical lines.

**Approach:** Two pointers, shrink from wider side
```python
def maxArea(height):
    left, right = 0, len(height) - 1
    max_area = 0
    
    while left < right:
        width = right - left
        h = min(height[left], height[right])
        max_area = max(max_area, width * h)
        
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    
    return max_area
```

**Time:** O(n), **Space:** O(1)

---

## Problem 3: Word Break (Medium) - 139
**Problem:** Check if string can be segmented into dictionary words.

**Approach:** BFS/DP - word break pattern
```python
def wordBreak(s, wordDict):
    word_set = set(wordDict)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True
    
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break
    
    return dp[n]
```

**Time:** O(n²), **Space:** O(n)

---

## Key Insights

1. **Sort + merge** - Classic interval problem, sort first
2. **Two pointers** - Shrink from larger height to find better area
3. **DP for segmentation** - dp[i] = can break s[:i], check all possible cuts

**Topics:** Intervals, Two Pointers, Dynamic Programming