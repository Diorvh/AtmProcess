import numpy as np

def find_last_negative(arr):
    """
    找到从右往左第一个小于0的数字

    参数:
    arr (np.array): 输入的一维NumPy数组

    返回:
    int: 从右往左第一个小于0的数字的索引，如果不存在返回-1
    """
    reversed_arr = arr[::-1]  # 反转数组
    indices = np.where(reversed_arr < 0)[0]
    if indices.size > 0:
        last_negative_index = arr.size - indices[0] - 1  # 计算从右往左的索引
        return last_negative_index
    else:
        return -1

# 示例数组
arr = np.array([1, 2, 3, -1, 4, 5, -2, 6, 7])

# 调用函数并打印结果
result_index = find_last_negative(arr)
if result_index != -1:
    print(f"从右往左第一个小于0的数字的索引是：{result_index}，其值为：{arr[result_index]}")
else:
    print("数组中没有小于0的数字。")
