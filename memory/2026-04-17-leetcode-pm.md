# LeetCode Practice - 2026-04-17 Afternoon

## Problem 1: Longest Palindromic Substring (Medium) - 5
**Problem:** Find the longest palindromic substring in s.

**Approach:** Expand around center
```python
def longestPalindrome(s):
    result = ""
    max_len = 0
    
    for i in range(len(s)):
        # Odd length palindromes
        l = r = i
        while l >= 0 and r < len(s) and s[l] == s[r]:
            if r - l + 1 > max_len:
                result = s[l:r+1]
                max_len = r - l + 1
            l -= 1
            r += 1
        
        # Even length palindromes
        l, r = i, i + 1
        while l >= 0 and r < len(s) and s[l] == s[r]:
            if r - l + 1 > max_len:
                result = s[l:r+1]
                max_len = r - l + 1
            l -= 1
            r += 1
    
    return result
```

**Time:** O(n²), **Space:** O(1)

---

## Problem 2: Edit Distance (Hard) - 72
**Problem:** Min edits to convert word1 to word2.

**Approach:** DP - insert, delete, or replace
```python
def minDistance(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i  # Delete all
    for j in range(n + 1):
        dp[0][j] = j  # Insert all
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],    # delete
                    dp[i][j-1],    # insert
                    dp[i-1][j-1]   # replace
                )
    
    return dp[m][n]
```

**Time:** O(m*n), **Space:** O(m*n)

---

## Key Insights

1. **Expand around center** — For palindrome, try odd and even centers, expand while chars match
2. **2D DP table** — Edit distance: dp[i][j] = min edits for first i chars of word1 to first j chars of word2
3. **Diagonal dependency** — When chars match, inherit from dp[i-1][j-1]

**Topics:** Strings, Dynamic Programming, Two Pointers