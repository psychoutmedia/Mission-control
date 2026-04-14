# LeetCode Practice — 2026-04-14 Evening

## Session: Strings & Dynamic Programming

---

### 1. Longest Palindromic Substring (5) — Medium

**Problem:** Given a string `s`, find the longest palindromic substring.

**Approach:** Expand around center. For each position, expand outward while chars match. Track longest.

```python
def longestPalindrome(s: str) -> str:
    longest = ""
    
    for i in range(len(s)):
        # Odd length palindrome (center on single char)
        l, r = i, i
        while l >= 0 and r < len(s) and s[l] == s[r]:
            if r - l + 1 > len(longest):
                longest = s[l:r+1]
            l -= 1
            r += 1
        
        # Even length palindrome (center between two chars)
        l, r = i, i + 1
        while l >= 0 and r < len(s) and s[l] == s[r]:
            if r - l + 1 > len(longest):
                longest = s[l:r+1]
            l -= 1
            r += 1
    
    return longest
```

**Complexity:** O(n²) time, O(1) space  
**Key insight:** Every palindrome has a center. Expanding around center handles both odd and even lengths elegantly.

**DP alternative (slower):**
```python
# dp[i][j] = True if s[i:j+1] is palindrome
# dp[i][j] = s[i] == s[j] and (j - i < 2 or dp[i+1][j-1])
# Build bottom-up from shorter to longer substrings
```

---

### 2. Edit Distance (72) — Hard

**Problem:** Convert `word1` to `word2` using insert, delete, replace operations. Min operations.

**Approach:** DP where `dp[i][j]` = min operations to convert `word1[:i]` to `word2[:j]`.

```python
def minDistance(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    
    # dp[i][j] = min edit distance from word1[:i] to word2[:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Base cases: converting to/from empty string
    for i in range(m + 1):
        dp[i][0] = i  # delete all i chars
    for j in range(n + 1):
        dp[0][j] = j  # insert all j chars
    
    # Fill table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]  # no op needed
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],    # delete from word1
                    dp[i][j-1],    # insert into word1
                    dp[i-1][j-1]   # replace
                )
    
    return dp[m][n]
```

**Complexity:** O(m×n) time and space  
**Key insight:** Bottom-up DP. Base cases handle empty strings. Three operations at each cell.

---

### 3. Word Break (139) — Medium

**Problem:** Given a string `s` and a dictionary of words, determine if `s` can be segmented into a space-separated sequence of dictionary words.

**Approach:** DP where `dp[i]` = True if `s[:i]` can be segmented.

```python
def wordBreak(s: str, wordDict: list[str]) -> bool:
    word_set = set(wordDict)
    n = len(s)
    
    # dp[i] = True if s[:i] can be segmented
    dp = [False] * (n + 1)
    dp[0] = True  # empty string is always segmentable
    
    for i in range(1, n + 1):
        for j in range(i):
            # Check if s[j:i] is in dictionary AND s[:j] is segmentable
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break  # Found valid segmentation, no need to check more
    
    return dp[n]
```

**Complexity:** O(n²) time, O(n) space  
**Optimization:** Can use BFS or Trie for O(n × max_word_len) instead of O(n²)

**BFS approach:**
```python
from collections import deque

word_set = set(wordDict)
queue = deque([0])
visited = {0}

while queue:
    start = queue.popleft()
    for end in range(start + 1, n + 1):
        if end not in visited and s[start:end] in word_set:
            if end == n:
                return True
            queue.append(end)
            visited.add(end)
return False
```

---

## Summary

| Problem | Difficulty | Time | Space | Pattern |
|---------|-----------|------|-------|---------|
| Longest Palindromic Substring | Medium | O(n²) | O(1) | Expand Around Center |
| Edit Distance | Hard | O(m×n) | O(m×n) | 2D DP |
| Word Break | Medium | O(n²) | O(n) | 1D DP |

**Total:** 3 problems — expand-around-center, 2D DP, BFS

**Patterns reinforced:**
- Expand around center: elegant for palindrome problems
- 2D DP: string transformation problems (edit distance, longest common subsequence)
- 1D DP with substring check: segmentation, word breaking
- BFS on string indices: alternative to DP for word break

**Next session:** Trees (Trie problems), Graph algorithms, or system design practice
