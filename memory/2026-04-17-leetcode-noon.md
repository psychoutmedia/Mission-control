# LeetCode Practice - 2026-04-17 Midday Session

## Problem 1: Binary Tree Level Order Traversal (Medium) - 102
**Problem:** Return level-by-level traversal of a binary tree.

**Approach:** BFS with level tracking
```python
def levelOrder(root):
    if not root:
        return []
    
    result = []
    queue = [root]
    
    while queue:
        level_size = len(queue)
        level = []
        
        for _ in range(level_size):
            node = queue.pop(0)
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        result.append(level)
    
    return result
```

**Time:** O(n), **Space:** O(w) where w = max width

---

## Problem 2: Validate Binary Search Tree (Medium) - 98
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

**Time:** O(n), **Space:** O(h) for recursion

---

## Problem 3: Coin Change (Medium) - 322
**Problem:** Find minimum coins needed to reach amount.

**Approach:** BFS or DP bottom-up
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

1. **BFS for level order** — Track level size to process by level
2. **BST validation** — Pass min/max bounds, not just parent value
3. **Bottom-up DP** — Build solution from smaller subproblems
4. **Infinity for unreachable** — Use float('inf') for impossible states in DP

**Topics:** Trees, BFS, Dynamic Programming, Graph traversal