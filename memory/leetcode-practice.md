# LeetCode Practice — 5 Medium Array/String Problems

> Created: 2026-03-06

Practice these 5 problems to build algorithmic thinking for interviews.

---

## Problem 1: 3Sum (Medium)

**LeetCode**: #15
**Link**: https://leetcode.com/problems/3sum/

### Problem
Given an integer array nums, return all the triplets `[nums[i], nums[j], nums[k]]` such that `i != j`, `j != k`, and `i != k`, and `nums[i] + nums[j] + nums[k] == 0`.

### Solution

```python
def threeSum(nums):
    nums.sort()
    result = []
    n = len(nums)
    
    for i in range(n - 2):
        # Skip duplicates for first element
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        
        # Two-pointer approach for remaining two
        left, right = i + 1, n - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                result.append([nums[i], nums[left], nums[right]])
                # Skip duplicates
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1
    
    return result
```

**Time**: O(n²) | **Space**: O(1) extra (excluding output)

---

## Problem 2: Longest Substring Without Repeating Characters (Medium)

**LeetCode**: #3
**Link**: https://leetcode.com/problems/longest-substring-without-repeating-characters/

### Problem
Given a string `s`, find the length of the **longest substring** without repeating characters.

### Solution

```python
def lengthOfLongestSubstring(s):
    char_index = {}  # Store last seen index of each char
    max_length = 0
    start = 0
    
    for end, char in enumerate(s):
        # If char seen and is within current window, shrink window
        if char in char_index and char_index[char] >= start:
            start = char_index[char] + 1
        
        # Update last seen index
        char_index[char] = end
        
        # Update max length
        max_length = max(max_length, end - start + 1)
    
    return max_length
```

**Time**: O(n) | **Space**: O(min(n, alphabet_size))

---

## Problem 3: Container With Most Water (Medium)

**LeetCode**: #11
**Link**: https://leetcode.com/problems/container-with-most-water/

### Problem
Given `n` non-negative integers `height[i]` where each represents a point at coordinate (i, height[i]). Find two lines that together with the x-axis form a container that contains the most water.

### Solution

```python
def maxArea(height):
    left = 0
    right = len(height) - 1
    max_water = 0
    
    while left < right:
        # Calculate current water
        h = min(height[left], height[right])
        width = right - left
        max_water = max(max_water, h * width)
        
        # Move the shorter line
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    
    return max_water
```

**Time**: O(n) | **Space**: O(1)

---

## Problem 4: Rotate Image (Medium)

**LeetCode**: #48
**Link**: https://leetcode.com/problems/rotate-image/

### Problem
You are given an `n x n` 2D matrix representing an image, rotate the image by 90 degrees (clockwise).

### Solution

```python
def rotate(matrix):
    n = len(matrix)
    
    # Transpose the matrix
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    
    # Reverse each row
    for row in matrix:
        row.reverse()
```

**Time**: O(n²) | **Space**: O(1)

**Visual**:
```
Original:      Transposed:    Reversed:
1 2 3         1 4 7         7 4 1
4 5 6    →    2 5 8    →    8 5 2
7 8 9         3 6 9         9 6 3
```

---

## Problem 5: Longest Palindromic Substring (Medium)

**LeetCode**: #5
**Link**: https://leetcode.com/problems/longest-palindromic-substring/

### Problem
Given a string `s`, return the longest palindromic substring in `s`.

### Solution

```python
def longestPalindrome(s):
    if len(s) <= 1:
        return s
    
    start, max_len = 0, 1
    
    # Expand around center
    def expand(left, right):
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return right - left - 1
    
    for i in len(s):
        # Odd length palindrome
        len1 = expand(i, i)
        # Even length palindrome
        len2 = expand(i, i + 1)
        
        cur_max = max(len1, len2)
        if cur_max > max_len:
            start = i - (cur_max - 1) // 2
            max_len = cur_max
    
    return s[start:start + max_len]
```

**Time**: O(n²) | **Space**: O(1)

---

## Key Patterns to Remember

| Pattern | Problems |
|---------|----------|
| Two pointers | 3Sum, Container With Most Water |
| Sliding window | Longest Substring Without Repeating |
| In-place matrix | Rotate Image |
| Expand around center | Longest Palindromic Substring |
| Hash map | Longest Substring |

---

## Practice Strategy

1. **Understand the pattern** — don't just memorize solutions
2. **Dry run** — trace through with example inputs
3. **Time complexity** — always consider O(n) vs O(n²)
4. **Edge cases** — empty input, single element, duplicates

---

*Practice makes pattern recognition automatic.* ✨
