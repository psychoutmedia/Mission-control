# LeetCode Practice - March 9, 2026

## Goal
Practice 3 medium problems to build algorithmic thinking for LLM engineering interviews.

---

## Problem 1: Valid Parentheses (Medium)
**LeetCode #20**

### Description
Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, determine if the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order.
3. Every close bracket has a corresponding open bracket of the same type.

### Example
```
Input: s = "()[]{}"
Output: true

Input: s = "(]"
Output: false
```

### Solution
```python
def isValid(s: str) -> bool:
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in mapping:
            if not stack or stack.pop() != mapping[char]:
                return False
        else:
            stack.append(char)
    
    return not stack
```

### Complexity
- Time: O(n)
- Space: O(n)

---

## Problem 2: Longest Substring Without Repeating Characters (Medium)
**LeetCode #3**

### Description
Given a string `s`, find the length of the longest substring without repeating characters.

### Example
```
Input: s = "abcabcbb"
Output: 3
Explanation: The answer is "abc", with length 3.

Input: s = "bbbbb"
Output: 1
Explanation: The answer is "b", with length 1.
```

### Solution
```python
def lengthOfLongestSubstring(s: str) -> int:
    char_index = {}
    max_length = 0
    start = 0
    
    for end, char in enumerate(s):
        if char in char_index and char_index[char] >= start:
            start = char_index[char] + 1
        
        char_index[char] = end
        max_length = max(max_length, end - start + 1)
    
    return max_length
```

### Complexity
- Time: O(n)
- Space: O(min(m, n)) where m = charset size

### Key Insight
Sliding window technique with hash map to track character positions.

---

## Problem 3: Container With Most Water (Medium)
**LeetCode #11**

### Description
You are given an integer array `height` of length `n`. There are `n` vertical lines drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i]).

Find two lines that together with the x-axis form a container, such that the container contains the most water.

Return the maximum amount of water a container can store.

### Example
```
Input: height = [1,8,6,2,5,4,8,3,7]
Output: 49
Explanation: The max area is between height[1]=8 and height[8]=7.
```

### Solution
```python
def maxArea(height: list[int]) -> int:
    left = 0
    right = len(height) - 1
    max_water = 0
    
    while left < right:
        width = right - left
        h = min(height[left], height[right])
        max_water = max(max_water, width * h)
        
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    
    return max_water
```

### Complexity
- Time: O(n)
- Space: O(1)

### Key Insight
Two-pointer approach from both ends. Always move the shorter line inward.

---

## Summary

| Problem | Technique | Difficulty |
|---------|-----------|------------|
| Valid Parentheses | Stack | Medium |
| Longest Substring | Sliding Window + HashMap | Medium |
| Container With Most Water | Two Pointers | Medium |

**Total practiced: 3 problems**
