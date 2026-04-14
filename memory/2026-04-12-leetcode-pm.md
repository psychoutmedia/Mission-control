# LeetCode Medium Problems — 2026-04-12 PM

Sunday afternoon session — three binary search and sliding window problems.

---

## 1. Search in Rotated Sorted Array
**LeetCode #33** | Pattern: Binary Search (with rotation twist)

### Problem
There is an integer array `nums` sorted in ascending order (with distinct values). Prior to being passed to your function, `nums` is possibly rotated. Given the list `nums` after the possible rotation and an integer `target`, return the index of `target` if it is in `nums`, or `-1` if it is not.

### Solution

```python
def search(nums: list[int], target: int) -> int:
    """
    Modified binary search.
    At each step, one half is guaranteed to be sorted.
    Determine which half contains target by comparing with boundary values.
    """
    lo, hi = 0, len(nums) - 1

    while lo <= hi:
        mid = (lo + hi) // 2

        if nums[mid] == target:
            return mid

        # Determine which half is sorted
        if nums[lo] <= nums[mid]:
            # Left half is sorted
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            # Right half is sorted
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1

    return -1
```

### Key Insights
- **The rotation breaks naive binary search** — but at any midpoint, at least one half is always sorted.
- `nums[lo] <= nums[mid]` tells us the left half is sorted (if `lo <= mid`, no gap = no rotation in left).
- Once we know which half is sorted, we can check if target falls within that half's range.
- O(log n) — classic binary search but with a pivot check.

### Edge Cases
- `nums = [4,5,6,7,0,1,2]`, target = 0 → index 4
- `nums = [4,5,6,7,0,1,2]`, target = 3 → -1
- Single element: `nums = [1]`, target = 0 → -1

### Complexity
| Time | Space |
|---|---|
| O(log n) | O(1) |

---

## 2. Minimum Size Subarray Sum
**LeetCode #209** | Pattern: Sliding Window (two pointers)

### Problem
Given an array of positive integers `nums` and a positive integer `s`, return the minimal length of a contiguous subarray of which the sum is at least `s`. If there is no such subarray, return 0.

### Solution

```python
def minSubArrayLen(s: int, nums: list[int]) -> int:
    """
    Sliding window — expand right, shrink left.
    Keep a running sum. When sum >= s, try shrinking from the left
    while maintaining the sum >= s condition. Track min length.
    """
    n = len(nums)
    left = 0
    current_sum = 0
    min_len = float('inf')

    for right in range(n):
        current_sum += nums[right]

        # Try to shrink window while condition still holds
        while current_sum >= s:
            min_len = min(min_len, right - left + 1)
            current_sum -= nums[left]
            left += 1

    return 0 if min_len == float('inf') else min_len
```

### Key Insights
- **Sliding window** is optimal when all numbers are positive (guarantees shrinking makes sum smaller).
- Expand right pointer to include more elements → when condition met, shrink left to find minimum.
- Each element entered once (right moves forward) and removed once (left moves forward) → O(n).

### Complexity
| Time | Space |
|---|---|
| O(n) | O(1) |

---

## 3. Longest Substring Without Repeating Characters
**LeetCode #3** | Pattern: Sliding Window with Hash Set

### Problem
Given a string `s`, find the length of the longest substring without repeating characters.

### Solution

```python
def lengthOfLongestSubstring(s: str) -> int:
    """
    Sliding window with character index tracking.
    When we see a duplicate, move left pointer past the previous occurrence.
    Use a dict to store the last index of each character.
    """
    char_index = {}  # char -> most recent index
    left = 0
    max_len = 0

    for right, char in enumerate(s):
        # If char is in window, slide left past previous occurrence
        if char in char_index and char_index[char] >= left:
            left = char_index[char] + 1

        char_index[char] = right
        max_len = max(max_len, right - left + 1)

    return max_len
```

### Key Insights
- **Two variations**: naive (check all substrings O(n³)), hash set only (O(2n)), or hash map with left pointer (O(n)) — the map version is optimal.
- When we encounter a duplicate, we can safely jump `left` to `previous_occurrence + 1` because everything before that is still a valid window.
- The `char_index[char] >= left` check is critical — if the previous occurrence is already outside the current window, we ignore it.

### Examples
- `"abcabcbb"` → 3 (`"abc"`)
- `"bbbbb"` → 1 (`"b"`)
- `"pwwkew"` → 3 (`"wke"`)
- `" "` → 1 (single space)
- `""` → 0

### Complexity
| Time | Space |
|---|---|
| O(n) — single pass | O(min(m, n)) — m = charset size (26 for letters, 128 for ASCII, 256 for extended) |

---

## Summary

| Problem | Pattern | Key Concept |
|---|---|---|
| Search in Rotated Array | Binary Search | One half always sorted; check which half contains target |
| Min Size Subarray Sum | Sliding Window | Expand right, shrink left when condition met |
| Longest Substring (No Repeat) | Sliding Window + Hash Map | Jump left pointer past duplicate's last occurrence |

Two distinct but complementary patterns:
- **Binary search** — divide and conquer, logarithmic time, works on sorted/rotated data
- **Sliding window** — expand/shrink two pointers, linear time, great for subarray/substring problems
