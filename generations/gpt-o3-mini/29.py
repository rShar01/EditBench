def some_func():
    # Example sorted list and target for binary search
    arr = [1, 3, 5, 7, 9, 11, 13]
    target = 7

    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return f"Found {target} at index {mid}."
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return f"{target} not found."


print(
    some_func()
)
