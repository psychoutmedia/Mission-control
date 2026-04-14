# LeetCode Practice — 2026-04-14 PM

## Session: Two Pointers & Sliding Window

---

### 1. Valid Palindrome II (680) — Medium

**Problem:** Given a string `s`, return `True` if it can become a palindrome after deleting **at most one** character.

**Approach:** Two pointers from both ends. When mismatch found, try skipping either left or right char and check remaining substring.

```python
def validPalindrome(s: str) -> bool:
    def is_palindrome(l, r):
        while l < r:
            if s[l] != s[r]:
                return False
            l += 1
            r -= 1
        return True
    
    l, r = 0, len(s) - 1
    while l < r:
        if s[l] == s[r]:
            l += 1
            r -= 1
        else:
            # Try skipping either side
            return is_palindrome(l + 1, r) or is_palindrome(l, r - 1)
    return True
```

**Complexity:** O(n) time, O(1) space  
**Key insight:** Only need to check one deletion — the palindrome property is restored if remaining chars match.

---

### 2. Longest Substring Without Repeating (3) — Medium

**Problem:** Find the length of the longest substring with all unique characters.

**Approach:** Sliding window with hash map storing last seen index of each character. Expand window right, shrink from left when duplicate found.

```python
def lengthOfLongestSubstring(s: str) -> int:
    char_index = {}  # char -> last seen index
    left = 0
    max_len = 0
    
    for right, char in enumerate(s):
        # Shrink window if we've seen this char in current window
        if char in char_index and char_index[char] >= left:
            left = char_index[char] + 1
        
        char_index[char] = right
        max_len = max(max_len, right - left + 1)
    
    return max_len
```

**Complexity:** O(n) time, O(min(n, 26)) space (alphabet size)  
**Key insight:** Using `char_index[char] >= left` instead of `in char_index` handles repeated chars outside current window.

---

### 3. Minimum Window Substring (76) — Hard

**Problem:** Given two strings `s` and `t`, find the minimum window substring in `s` that contains all characters of `t`.

**Approach:** Sliding window with frequency counter. Expand right to include chars, contract left when window is valid.

```python
def minWindow(s: str, t: str) -> str:
    from collections import Counter
    
    need = Counter(t)
    window = Counter()
    have = 0
    required = len(need)
    result = (float('inf'), None, None)  # (length, start, end)
    left = 0
    
    for right, char in enumerate(s):
        window[char] += 1
        if char in need and window[char] == need[char]:
            have += 1
        
        # Contract window while it's valid
        while have == required:
            # Update result
            if right - left + 1 < result[0]:
                result = (right - left + 1, left, right)
            
            # Remove left char and try shrinking
            left_char = s[left]
            if left_char in need and window[left_char] == need[left_char]:
                have -= 1
            window[left_char] -= 1
            left += 1
    
    return s[result[1]:result[2]+1] if result[1] is not None else ""
```

**Complexity:** O(n) time (each char visited at most twice), O(1) space (counter size bounded by charset)  
**Key insight:** The `have == required` condition triggers contraction — we only shrink when window contains all required chars.

---

## Summary

| Problem | Difficulty | Time | Space | Pattern |
|---------|-----------|------|-------|---------|
| Valid Palindrome II | Medium | O(n) | O(1) | Two Pointers |
| Longest Substring | Medium | O(n) | O(min(n,m)) | Sliding Window |
| Minimum Window | Hard | O(n) | O(1) | Sliding Window + Counter |

**Total:** 3 problems, 3 different sliding window variations

**Patterns reinforced:**
- Two pointers: great for palindrome, pair matching
- Sliding window: expand right, contract left when condition breaks
- Hash map + index tracking for O(1) lookups

**Next session:** Consider Strings/DP problems (Longest Palindromic Substring, Edit Distance)
