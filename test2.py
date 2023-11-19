import numpy as np

def find_last_greater_equal(arr, thres):
    """
    找到从右往左第一个大于等于阈值的元素的位置

    参数:
    arr (np.array): 输入的一维NumPy数组
    thres (int or float): 阈值

    返回:
    int: 从右往左第一个大于等于阈值的元素的位置，如果不存在返回-1
    """
    reversed_arr = arr[::-1]  # 反转数组
    indices = np.where(reversed_arr >= thres)[0]
    if indices.size > 0:
        last_index = arr.size - indices[0] - 1  # 计算从右往左的索引
        return last_index
    else:
        return -1

# 示例数组和阈值
arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
threshold = 5

# 调用函数并打印结果
result_index = find_last_greater_equal(arr, threshold)
if result_index != -1:
    print(f"从右往左第一个大于等于阈值的元素的位置是：{result_index}，其值为：{arr[result_index]}")
else:
    print(f"数组中不存在大于等于阈值 {threshold} 的元素。")
