#include <Eigen/Dense>
#include <vector>
#include <iostream>

std::vector<double> savitzkyGolayFilter_1st(const std::vector<double>& data, int window_length) {//一阶S-G滤波器，与py一致，边界采用interp方法，直接拟合边界window_length个点得到的函数，预测边界上window_length//2个点的数值
    int data_size = data.size();
    std::vector<double> filtered_data(data_size, 0.0);

    for (int i = 0; i < data_size; ++i) {
        int window_start = std::max(i - window_length / 2, 0);
        int window_end = std::min(window_start + window_length, data_size);
        window_start = std::max(window_end - window_length, 0);  // Adjust start for the boundary points

        int window_size = window_end - window_start;
        Eigen::VectorXd y(window_size);
        Eigen::MatrixXd X(window_size, 2);

        for (int j = window_start; j < window_end; ++j) {
            y(j - window_start) = data[j];
            X(j - window_start, 0) = 1.0;
            X(j - window_start, 1) = j - i; // Centered at the current point i
        }

        Eigen::Vector2d beta = (X.transpose() * X).ldlt().solve(X.transpose() * y);
        filtered_data[i] = beta(0); // The fitted value at the central point
    }

    return filtered_data;
}
/*
int main() {
    std::vector<double> data = {2, 2, 5, 2, 1, 0, 1, 4, 9};
    int window_length = 5;
    clock_t start_time=clock();//计时
    std::vector<double> filtered_data = savitzkyGolayFilter_1st(data, window_length);
    std:: cout << "The run time is: " <<(double)(clock() - start_time) / CLOCKS_PER_SEC << "s" << std::endl;//计时
    for (double d : filtered_data) {
        std::cout << d << " ";
    }
    std::cout << std::endl;

    return 0;
}
*/