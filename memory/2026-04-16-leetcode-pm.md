# LeetCode Practice — 2026-04-16 Afternoon

**Time:** 1:02 PM
**Topic:** Binary Search & Divide & Conquer (Medium)
**Session goal:** 3 medium problems

---

## Problem 1: Find Minimum in Rotated Sorted Array (LC 153)

```python
def findMin(nums):
    left, right = 0, len(nums) - 1
    
    while left < right:
        mid = (left + right) // 2
        if nums[mid] > nums[right]:
            left = mid + 1
        else:
            right = mid
    
    return nums[left]
```

**Key insight:** Classic rotated array search. The pivot is where nums[mid] > nums[right].
If mid > right, minimum is to the right. Else, minimum is at mid or left.

**Complexity:** O(log n) time, O(1) space

---

## Problem 2: Search in Rotated Sorted Array II (LC 81) — with duplicates

```python
def search(nums, target):
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return True
        
        # Skip duplicates on left side
        if nums[left] == nums[mid] == nums[right]:
            left += 1
        elif nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    
    return False
```

**Key insight:** Same as LC 33 but with duplicates. When nums[left] == nums[mid] == nums[right],
we can't determine which side is sorted → increment left. This makes it O(n) worst case.

**Complexity:** O(log n) average, O(n) worst case (with duplicates), O(1) space

---

## Problem 3: Median of Two Sorted Arrays (LC 4) — Hard

```python
def findMedianSortedArrays(nums1, nums2):
    # Ensure nums1 is the shorter array
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    
    m, n = len(nums1), len(nums2)
    left, right = 0, m
    median1, median2 = 0, 0
    
    while left <= right:
        # Partition points
        i = (left + right) // 2
        j = (m + n + 1) // 2 - i
        
        # Get border values
        nums1_left = nums1[i-1] if i > 0 else float('-inf')
        nums1_right = nums1[i] if i < m else float('inf')
        nums2_left = nums2[j-1] if j > 0 else float('-inf')
        nums2_right = nums2[j] if j < n else float('inf')
        
        # Binary search logic
        if nums1_left <= nums2_right and nums2_left <= nums1_right:
            # Found correct partition
            if (m + n) % 2 == 0:
                return (max(nums1_left, nums2_left) + min(nums1_right, nums2_right)) / 2
            else:
                return max(nums1_left, nums2_left)
        elif nums1_left > nums2_right:
            right = i - 1
        else:
            left = i + 1
    
    return 0
```

**Key insight:** Binary search on the smaller array to find the partition. The partition must satisfy:
- Left side has (m+n+1)//2 elements
- All left elements <= all right elements

This is O(log(min(m,n))) — the gold standard for binary search problems.

**Complexity:** O(log(min(m, n))) time, O(1) space

---

## Summary

| Problem | Key Insight |
|---------|-------------|
| Find Min (LC 153) | Pivot detection: nums[mid] > nums[right] |
| Search Rotated II (LC 81) | Duplicate handling: skip when all three equal |
| Median of Sorted Arrays (LC 4) | Binary search on partition, O(log(min(m,n))) |

**Why this matters for LLM Engineering:**
- Binary search is fundamental to attention mechanisms (searching context)
- Divide and conquer underlies transformer architecture
- Median finding = percentile calculations for RLHF reward modeling

**Next session:** String algorithms or matrix/Dynamic Programming 2D problems.
