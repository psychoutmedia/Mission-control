# LeetCode Practice — 2026-04-16 Evening

**Time:** 6:13 PM
**Topic:** Greedy & Intervals (Medium)
**Session goal:** 3 medium problems

---

## Problem 1: Non-overlapping Intervals (LC 435)

```python
def eraseOverlapIntervals(intervals):
    if not intervals:
        return 0
    
    # Sort by end time (greedy: remove intervals that end latest)
    intervals.sort(key=lambda x: x[1])
    
    count = 0
    end = intervals[0][1]
    
    for i in range(1, len(intervals)):
        start, cur_end = intervals[i]
        if start < end:  # Overlap
            count += 1
        else:
            end = cur_end  # No overlap, update end
    
    return count
```

**Key insight:** Sort by end time. Greedily keep intervals that end earliest.
Remove the one that overlaps and ends later. Classic "minimum removals" pattern.

**Complexity:** O(n log n) time (sorting), O(1) space

---

## Problem 2: Meeting Rooms II (LC 253)

```python
import heapq

def minMeetingRooms(intervals):
    if not intervals:
        return 0
    
    # Sort by start time
    intervals.sort(key=lambda x: x[0])
    
    # Min-heap of end times
    heap = [intervals[0][1]]
    
    for start, end in intervals[1:]:
        # If earliest ending room is free, reuse it
        if start >= heap[0]:
            heapq.heappop(heap)
        # Add current meeting
        heapq.heappush(heap, end)
    
    return len(heap)
```

**Key insight:** Sort by start, use min-heap of end times.
If earliest ending room is free before current starts, reuse it.
Otherwise, need a new room.

**Complexity:** O(n log n) time, O(n) space

---

## Problem 3: Gas Station (LC 134)

```python
def canCompleteCircuit(gas, cost):
    total_tank = 0
    curr_tank = 0
    start = 0
    
    for i in range(len(gas)):
        diff = gas[i] - cost[i]
        total_tank += diff
        curr_tank += diff
        
        if curr_tank < 0:
            # Can't start from any station between start and i
            start = i + 1
            curr_tank = 0
    
    return start if total_tank >= 0 else -1
```

**Key insight:** If total gas >= total cost, solution exists.
If current tank goes negative at index i, reset start to i+1.
The key insight: if we can't get from A to B, we can't start from any station between A and B.

**Complexity:** O(n) time, O(1) space

---

## Summary

| Problem | Greedy Strategy | Key Insight |
|---------|-----------------|-------------|
| Non-overlapping Intervals (LC 435) | Sort by end time | Remove latest-ending overlapping interval |
| Meeting Rooms II (LC 253) | Min-heap of end times | Reuse earliest-free room |
| Gas Station (LC 134) | Track total and current | If tank < 0 at i, can't start from A..i |

**Why this matters for LLM Engineering:**
- Greedy = beam search decisions (pick best token)
- Interval scheduling = resource allocation in LLM serving
- Tank tracking = cumulative attention budget management

**Today Total:** 6 LeetCode sessions — 18 problems. Excellent day.
