#include <opencv2/opencv.hpp>
#include <algorithm>
double interpolate1D(double x, double x1, double y1, double x2, double y2) {
    if (x1 == x2) {
        return y1;
    } else {
        return (x2 - x) / (x2 - x1) * y1 + (x - x1) / (x2 - x1) * y2;
    }
}

double interpolate2D(const cv::Mat& data, double x, double y) {
    int x1 = static_cast<int>(std::floor(x));
    int x2 = std::min(x1 + 1, data.rows - 1);
    int y1 = static_cast<int>(std::floor(y));
    int y2 = std::min(y1 + 1, data.cols - 1);
    double z1 = interpolate1D(x, x1, data.at<ushort>(x1, y1), x2, data.at<ushort>(x2, y1));
    double z2 = interpolate1D(x, x1, data.at<ushort>(x1, y2), x2, data.at<ushort>(x2, y2));

    return interpolate1D(y, y1, z1, y2, z2);
}