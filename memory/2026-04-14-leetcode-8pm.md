# LeetCode Practice — 2026-04-14 Evening (8pm)

## Session: Binary Search & Divide & Conquer

---

### 1. Search in Rotated Sorted Array (33) — Medium

**Problem:** Given a rotated sorted array (e.g., [4,5,6,7,0,1,2]) and a target, return the index of target, or -1 if not found. O(log n) required.

**Approach:** Modified binary search. Determine which half is sorted, then check if target lies within the sorted half.

```python
def search(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if nums[mid] == target:
            return mid
        
        # Determine which half is sorted
        if nums[left] <= nums[mid]:
            # Left half is sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            # Right half is sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    
    return -1
```

**Complexity:** O(log n) time, O(1) space  
**Key insight:** Exactly one half is always sorted. Check which half contains target.

---

### 2. Median of Two Sorted Arrays (4) — Hard

**Problem:** Find the median of two sorted arrays, overall O(log n) time.

**Approach:** Binary search on the smaller array. Partition both arrays such that left half ≤ right half.

```python
def findMedianSortedArrays(nums1: list[int], nums2: list[int]) -> float:
    # Ensure nums1 is smaller for binary search efficiency
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    
    m, n = len(nums1), len(nums2)
    left = 0
    right = m
    
    while left <= right:
        # Partition point in nums1
        partition1 = (left + right) // 2
        # Partition point in nums2 (total left elements = (m + n + 1) // 2)
        partition2 = (m + n + 1) // 2 - partition1
        
        # Get max left values (or -inf if partition at start)
        maxLeft1 = nums1[partition1 - 1] if partition1 > 0 else float('-inf')
        minRight1 = nums1[partition1] if partition1 < m else float('inf')
        
        maxLeft2 = nums2[partition2 - 1] if partition2 > 0 else float('-inf')
        minRight2 = nums2[partition2] if partition2 < n else float('inf')
        
        # Check if partition is correct
        if maxLeft1 <= minRight2 and maxLeft2 <= minRight1:
            # Found correct partition
            if (m + n) % 2 == 0:
                return (max(maxLeft1, maxLeft2) + min(minRight1, minRight2)) / 2
            else:
                return max(maxLeft1, maxLeft2)
        elif maxLeft1 > minRight2:
            # Need to move left in nums1
            right = partition1 - 1
        else:
            # Need to move right in nums1
            left = partition1 + 1
    
    raise ValueError("Input arrays are not sorted")
```

**Complexity:** O(log(min(m, n))) time, O(1) space  
**Key insight:** Binary search on smaller array. Partition both arrays so all left elements ≤ all right elements.

---

### 3. Koko Eating Bananas (875) — Medium

**Problem:** Koko eats k bananas per hour from a pile. Given piles[], find minimum k such that Koko can eat all bananas within h hours.

**Approach:** Binary search on k. Check if current speed allows eating all within h hours.

```python
def minEatingSpeed(piles: list[int], h: int) -> int:
    # Speed cannot be less than 1 or more than max(piles)
    left, right = 1, max(piles)
    
    def can_eat_at_speed(k: int) -> bool:
        hours = 0
        for pile in piles:
            # Ceiling division: (pile + k - 1) // k
            hours += (pile + k - 1) // k
        return hours <= h
    
    while left < right:
        mid = (left + right) // 2
        
        if can_eat_at_speed(mid):
            # Can eat at this speed, try slower
            right = mid
        else:
            # Need to eat faster
            left = mid + 1
    
    return left
```

**Complexity:** O(n log max(piles)) time, O(1) space  
**Key insight:** Binary search on eating speed. Hours = sum of ceil(pile / k) for each pile.

---

## Summary

| Problem | Difficulty | Time | Space | Pattern |
|---------|-----------|------|-------|---------|
| Search Rotated Array | Medium | O(log n) | O(1) | Modified Binary Search |
| Median of Two Sorted Arrays | Hard | O(log(min(m,n))) | O(1) | Binary Search + Partition |
| Koko Eating Bananas | Medium | O(n log max) | O(1) | Binary Search on Answer |

**Total:** 3 problems — binary search variations

**Patterns reinforced:**
- Binary search on answer (not just finding element)
- Modified binary search for rotated arrays
- Partition-based approach for sorted arrays
- Ceiling division for time calculations

**Next session:** Consider backtracking, greedy, or system design practice
