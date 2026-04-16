# LeetCode Practice — 2026-04-16 Noon

**Time:** 12:02 PM
**Topic:** Dynamic Programming (Medium)
**Session goal:** 3 medium problems

---

## Problem 1: Longest Increasing Subsequence (LC 300)

```python
def lengthOfLIS(nums):
    # O(n log n) binary search approach
    import bisect
    
    dp = []
    for num in nums:
        pos = bisect.bisect_left(dp, num)
        if pos == len(dp):
            dp.append(num)
        else:
            dp[pos] = num
    return len(dp)
```

**Key insight:** Patience sorting / binary search — O(n log n) vs O(n²) brute force.
Also know the O(n²) DP: `dp[i] = max(dp[j] + 1 for j < i if nums[j] < nums[i])`

**Complexity:** O(n log n) time, O(n) space

---

## Problem 2: Coin Change (LC 322)

```python
def coinChange(coins, amount):
    # Bottom-up DP
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    for coin in coins:
        for a in range(coin, amount + 1):
            dp[a] = min(dp[a], dp[a - coin] + 1)
    
    return dp[amount] if dp[amount] != float('inf') else -1
```

**Key insight:** Unbounded knapsack variant — each coin can be used unlimited times. Build up from 0 to amount.

**Complexity:** O(n × amount) time, O(amount) space

---

## Problem 3: Longest Common Subsequence (LC 1143)

```python
def longestCommonSubsequence(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    return dp[m][n]
```

**Key insight:** 2D DP table — diagonal movement when chars match, else max of left/top.
Space-optimizable to O(min(m,n)) with rolling arrays.

**Complexity:** O(m × n) time, O(m × n) space

---

## Summary

| Problem | DP Type | Key Insight |
|---------|---------|-------------|
| Longest Increasing Subsequence | LIS / Binary Search | Patience sorting |
| Coin Change | Unbounded Knapsack | Build up from 0 |
| Longest Common Subsequence | 2D Table | Diagonal on match |

**DP Patterns for LLM Engineering:**
- Sequence modeling (attention = soft DP)
- Token-level decisions (LLM sampling = DP over token space)
- Beam search = DP with pruning

**Next session:** Try Trie problems or jump to interval-based DP.
