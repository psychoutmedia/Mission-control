# LeetCode Practice - Medium Problems (Arrays/Strings)

*Date: 2026-03-07*

## Problem 1: 3Sum (Medium)
**LeetCode #15** - Find all unique triplets in the array that sum to zero.

```python
def threeSum(nums):
    nums.sort()
    result = []
    n = len(nums)
    
    for i in range(n - 2):
        # Skip duplicates
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        
        # Two-pointer for remaining two
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

# Test
print(threeSum([-1,0,1,2,-1,-4]))
# Output: [[-1,-1,2],[-1,0,1]]
```

**Key insight**: Sort + two-pointer. Skip duplicates after finding a valid triplet. O(n²) time.

---

## Problem 2: Longest Substring Without Repeating Characters (Medium)
**LeetCode #3** - Find length of longest substring without repeating chars.

```python
def lengthOfLongestSubstring(s):
    char_index = {}  # char -> most recent index
    max_len = 0
    start = 0
    
    for end, char in enumerate(s):
        # If char seen and is within current window, shrink window
        if char in char_index and char_index[char] >= start:
            start = char_index[char] + 1
        
        char_index[char] = end
        max_len = max(max_len, end - start + 1)
    
    return max_len

# Test
print(lengthOfLongestSubstring("abcabcbb"))  # 3 ("abc")
print(lengthOfLongestSubstring("bbbbb"))     # 1 ("b")
print(lengthOfLongestSubstring("pwwkew"))    # 3 ("wke")
```

**Key insight**: Sliding window with hash map. When duplicate found, move start past previous occurrence. O(n) time, O(min(m,n)) space.

---

## Problem 3: Container With Most Water (Medium)
**LeetCode #11** - Max area between vertical lines.

```python
def maxArea(height):
    left, right = 0, len(height) - 1
    max_water = 0
    
    while left < right:
        # Calculate width and height
        width = right - left
        h = min(height[left], height[right])
        
        max_water = max(max_water, width * h)
        
        # Move pointer with smaller height
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    
    return max_water

# Test
print(maxArea([1,8,6,2,5,4,8,3,7]))  # 49
```

**Key insight**: Two-pointer from ends. Always move the shorter line inward—moving the taller one can only decrease area. O(n) time.

---

## Summary

| Problem | Pattern | Time | Space |
|---------|---------|------|-------|
| 3Sum | Sort + Two-pointer | O(n²) | O(n) |
| Longest Unique Substring | Sliding Window + Hash | O(n) | O(min(n,m)) |
| Container With Most Water | Two-pointer from ends | O(n) | O(1) |

**Takeaway**: These patterns (two-pointer, sliding window) appear frequently in interviews.
