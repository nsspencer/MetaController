# distutils: language=c++
from libcpp.vector cimport vector


def partition(list arr, cmp, int low, int high):
    cdef int i = low - 1
    cdef int pivot = arr[high]

    for j in range(low, high):
        if cmp(arr[j], pivot) < 0:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

def quickSort(list _arr, cmp):
    cdef list arr = _arr[:]
    cdef int low, high
    stack = [(0, len(arr) - 1)]

    while stack:
        low, high = stack.pop()

        if low < high:
            pi = partition(arr, cmp, low, high)
            stack.extend([(low, pi - 1), (pi + 1, high)])

    return arr


cdef int MIN_MERGE = 32

cdef int calcMinRun(int n):
    cdef int r = 0
    while n >= MIN_MERGE:
        r |= n & 1
        n >>= 1
    return n + r

cdef void insertionSort(list arr, int left, int right, cmp):
    cdef int i, j
    for i in range(left + 1, right + 1):
        j = i
        while j > left and cmp(arr[j], arr[j - 1]) < 0:
            arr[j], arr[j - 1] = arr[j - 1], arr[j]
            j -= 1

cdef void merge(list arr, int l, int m, int r, cmp):
    cdef int len1 = m - l + 1, len2 = r - m
    cdef list left = []
    cdef list right = []
    cdef int i, j, k
    for i in range(0, len1):
        left.append(arr[l + i])
    for i in range(0, len2):
        right.append(arr[m + 1 + i])
    i, j, k = 0, 0, l
    while i < len1 and j < len2:
        if cmp(left[i], right[j]) <= 0:
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            j += 1
        k += 1
    while i < len1:
        arr[k] = left[i]
        k += 1
        i += 1
    while j < len2:
        arr[k] = right[j]
        k += 1
        j += 1

cpdef list timSort(list _arr, cmp):
    cdef list arr = _arr[:]  # Create a copy of the array
    cdef int n = len(arr)
    cdef int minRun = calcMinRun(n)
    cdef int start, end, size, left, mid, right
    for start in range(0, n, minRun):
        end = min(start + minRun - 1, n - 1)
        insertionSort(arr, start, end, cmp)
    size = minRun
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(n - 1, left + size - 1)
            right = min((left + 2 * size - 1), (n - 1))
            if mid < right:
                merge(arr, left, mid, right, cmp)
        size = 2 * size
    return arr  # Return the sorted copy


# no comparitor sorting:

cdef void insertionSort2(list arr, int left, int right):
    cdef int i, j
    for i in range(left + 1, right + 1):
        j = i
        while j > left and arr[j] < arr[j - 1]:
            arr[j], arr[j - 1] = arr[j - 1], arr[j]
            j -= 1

cdef void merge2(list arr, int l, int m, int r):
    cdef int len1 = m - l + 1, len2 = r - m
    cdef list left = []
    cdef list right = []
    cdef int i, j, k
    for i in range(0, len1):
        left.append(arr[l + i])
    for i in range(0, len2):
        right.append(arr[m + 1 + i])
    i, j, k = 0, 0, l
    while i < len1 and j < len2:
        if left[i] <= right[j]:
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            j += 1
        k += 1
    while i < len1:
        arr[k] = left[i]
        k += 1
        i += 1
    while j < len2:
        arr[k] = right[j]
        k += 1
        j += 1

cpdef list timSort2(list arr):
    cdef list arr_copy = arr[:]  # Create a copy of the array
    cdef int n = len(arr_copy)
    cdef int minRun = calcMinRun(n)
    cdef int start, end, size, left, mid, right
    for start in range(0, n, minRun):
        end = min(start + minRun - 1, n - 1)
        insertionSort2(arr_copy, start, end)
    size = minRun
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(n - 1, left + size - 1)
            right = min((left + 2 * size - 1), (n - 1))
            if mid < right:
                merge2(arr_copy, left, mid, right)
        size = 2 * size
    return arr_copy  # Return the sorted copy