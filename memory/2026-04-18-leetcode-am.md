# LeetCode Practice - 2026-04-18 Early Morning

## Problem 1: Two Sum (Easy) - 1
**Problem:** Find indices of two numbers that add up to target.

**Approach:** Hash map for O(n) solution
```python
def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

**Time:** O(n), **Space:** O(n)

---

## Problem 2: Maximum Subarray (Medium) - 53
**Problem:** Find contiguous subarray with largest sum.

**Approach:** Kadane's algorithm
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

## Problem 3: Best Time to Buy and Sell Stock (Easy) - 121
**Problem:** Find maximum profit from one transaction.

**Approach:** Track min price and max profit
```python
def maxProfit(prices):
    min_price = float('inf')
    max_profit = 0
    
    for price in prices:
        min_price = min(min_price, price)
        max_profit = max(max_profit, price - min_price)
    
    return max_profit
```

**Time:** O(n), **Space:** O(1)

---

## Key Insights

1. **Hash map for pairs** — Store seen numbers to find complements in O(1)
2. **Kadane's algorithm** — Reset if current sum goes negative, track max
3. **Track min/max** — Keep running min price, update max profit on each day

**Topics:** Arrays, Hash Map, Dynamic Programming (Kadane's)