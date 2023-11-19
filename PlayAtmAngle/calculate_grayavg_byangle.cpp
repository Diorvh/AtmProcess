#include <iostream>

int find_last_greater_equal(const int* arr, int size, int thres) {// 从数组的末尾开始遍历
    for (int i = size - 1; i >= 0; --i)
        if (arr[i] >= thres)// 找到第一个大于等于阈值的元素
            return i;
    return -1;// 如果没有找到，返回 -1
}

int main() {
    // 示例数组和阈值
    int arr[] = {1, 3, 5, 7, 1};
    int thres = 4;
    int size = sizeof(arr) / sizeof(arr[0]);

    // 调用函数并打印结果
    int result = find_last_greater_equal(arr, size, thres);
    std::cout << "Result: " << result << std::endl;

    return 0;
}
