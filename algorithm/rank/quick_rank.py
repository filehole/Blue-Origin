#!/usr/bin/python
# -*- coding:UTF-8 -*-

"""
快速排序
"""


def quick_sort(data, left, right):
    if left < right:
        pivot = partition(data, left, right)
        quick_sort(data, left, pivot - 1)
        quick_sort(data, pivot + 1, right)
    return data


def switch_two_element(data, index1, index2):
    temp = data[index1]
    data[index1] = data[index2]
    data[index2] = temp


def partition(data, left, right):
    pivot_value = data[left]
    while left < right:
        while (left < right) and (data[right] >= pivot_value):
            right = right - 1
        switch_two_element(data, left, right)
        while (left < right) and (data[left] <= pivot_value):
            left = left + 1
        switch_two_element(data, left, right)
    return left


if __name__ == "__main__":
    L = [13, 14, 94, 33, 82, 25, 59, 94, 65, 23, 45, 27, 73, 25, 39, 10]
    print quick_sort(L, 0, len(L) - 1)



