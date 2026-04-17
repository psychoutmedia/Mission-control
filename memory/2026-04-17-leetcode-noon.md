# LeetCode Practice - 2026-04-17 Midday

## Problem 1: Validate BST (Medium) - 98
**Problem:** Determine if a binary tree is a valid BST.

**Approach:** Recursive with min/max bounds
```python
def isValidBST(root, min_val=float('-inf'), max_val=float('inf')):
    if not root:
        return True
    
    if root.val <= min_val or root.val >= max_val:
        return False
    
    return (isValidBST(root.left, min_val, root.val) and
            isValidBST(root.right, root.val, max_val))
```

**Time:** O(n), **Space:** O(h)

---

## Problem 2: House Robber (Medium) - 198
**Problem:** Max money you can rob without robbing adjacent houses.

**Approach:** DP - rob or skip each house
```python
def rob(nums):
    prev_two = 0  # dp[i-2]
    prev_one = 0  # dp[i-1]
    
    for num in nums:
        curr = max(prev_one, prev_two + num)
        prev_two = prev_one
        prev_one = curr
    
    return prev_one
```

**Time:** O(n), **Space:** O(1)

---

## Problem 3: Coin Change (Medium) - 322
**Problem:** Min coins to reach amount.

**Approach:** Bottom-up DP
```python
def coinChange(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    for coin in coins:
        for i in range(coin, amount + 1):
            dp[i] = min(dp[i], dp[i - coin] + 1)
    
    return dp[amount] if dp[amount] != float('inf') else -1
```

**Time:** O(n * amount), **Space:** O(amount)

---

## Key Insights

1. **BST validation** — Pass bounds, not just parent value. Left subtree gets upper bound.
2. **House Robber** — Classic DP with rolling window. Only need prev_two and prev_one.
3. **Unbounded knapsack** — For coin change, iterate coins outer loop.

**Topics:** Trees (BST), Dynamic Programming, Recursion