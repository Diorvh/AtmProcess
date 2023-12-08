#include <iostream>
#include <cmath>
#include <vector>

using namespace std;

int find_last_greater_equal(const int* arr, int size, int thres) {// 从数组的末尾开始遍历
    for (int i = size - 1; i >= 0; --i)
        if (arr[i] >= thres)// 找到第一个大于等于阈值的元素
            return i;
    return -1;// 如果没有找到，返回 -1
}

int main() {
    vector<double> npsin;
    vector<double> npcos;

    for (int i = 0; i <= 1800; ++i) {
        double angle = (i * 0.1 + 0.05) / 180 * M_PI;
        npsin.push_back(sin(angle));
        npcos.push_back(cos(angle));
    }
    // 示例数组和阈值
    int arr[] = {1, 3, 5, 7, 1};
    int thres = 4;
    int size = sizeof(arr) / sizeof(arr[0]);

    // 调用函数并打印结果
    int result = find_last_greater_equal(arr, size, thres);
    std::cout << "Result: " << result << std::endl;

    return 0;
}
