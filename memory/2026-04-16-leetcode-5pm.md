# LeetCode Practice — 2026-04-16 Evening

**Time:** 5:13 PM
**Topic:** Stack & Monotonic Stack (Medium)
**Session goal:** 3 medium problems

---

## Problem 1: Daily Temperatures (LC 739)

```python
def dailyTemperatures(temperatures):
    n = len(temperatures)
    result = [0] * n
    stack = []  # (index, temperature)
    
    for i, temp in enumerate(temperatures):
        while stack and temp > stack[-1][1]:
            prev_idx, _ = stack.pop()
            result[prev_idx] = i - prev_idx
        stack.append((i, temp))
    
    return result
```

**Key insight:** Monotonic decreasing stack. For each day, pop warmer days from stack and record the difference.
Classic "next greater element" pattern.

**Complexity:** O(n) time, O(n) space

---

## Problem 2: Car Fleet (LC 853)

```python
def carFleet(target, positions, speeds):
    # Sort cars by position (descending)
    cars = sorted(zip(positions, speeds), reverse=True)
    stack = []  # Stack of arrival times
    
    for pos, speed in cars:
        # Time to reach target
        time = (target - pos) / speed
        stack.append(time)
        
        # If current car arrives at same or earlier time, same fleet
        if len(stack) >= 2 and stack[-1] <= stack[-2]:
            stack.pop()
    
    return len(stack)
```

**Key insight:** Sort by position descending, then compute time to reach target.
If a car catches up (arrives at same or earlier time), it's in the same fleet.
Uses stack to track fleet leaders.

**Complexity:** O(n log n) time (sorting), O(n) space

---

## Problem 3: Minimum Number of Swaps to Make the String Balanced (LC 1963)

```python
def minSwaps(s):
    # Count maximum imbalance: when close > open, we need a swap
    max imbalance = 0
    imbalance = 0
    swaps = 0
    
    for char in s:
        if char == '[':
            if imbalance > 0:
                swaps += imbalance  # Need 1 swap for each imbalanced ']'
                imbalance -= 1     # Swap fixes one ']'
            else:
                imbalance = 0
        else:  # char == ']'
            imbalance += 1
            max_imbalance = max(max_imbalance, imbalance)
    
    # For '[' at position i, it pairs with ']' at position i + imbalance + 1
    # Number of swaps = max imbalance encountered
    return max_imbalance // 2  # Each swap fixes 2 imbalances
```

**Actually, the cleaner formula:**

```python
def minSwaps(s):
    imbalance = 0
    max_imbalance = 0
    
    for char in s:
        if char == '[':
            if imbalance > 0:
                imbalance -= 1  # Each '[' fixes one ']'
        else:  # ']'
            imbalance += 1
        max_imbalance = max(max_imbalance, imbalance)
    
    # Each swap brings one '[' forward, fixing 2 imbalances
    return (max_imbalance + 1) // 2
```

**Key insight:** Track max imbalance. Each swap fixes 2 imbalances (brings '[' forward).
Formula: `(max_depth + 1) // 2`.

**Complexity:** O(n) time, O(1) space

---

## Summary

| Problem | Stack Pattern | Key Insight |
|---------|---------------|-------------|
| Daily Temperatures (LC 739) | Monotonic decreasing | Next greater element |
| Car Fleet (LC 853) | Stack of times | Sort desc, pop if catching up |
| Min Swaps Balanced (LC 1963) | Track imbalance | Max imbalance // 2 |

**Why this matters for LLM Engineering:**
- Monotonic stacks = attention span computation (processing sequences with constraints)
- The "next greater element" pattern appears in transformer attention masking
- Greedy + stack is fundamental for parsing and sequence processing

**Today Total:** 5 LeetCode sessions — Graphs, DP, Binary Search, Backtracking, Stack. Solid day.
