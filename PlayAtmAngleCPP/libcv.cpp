#include <opencv2/opencv.hpp>
#include <string>
#include <iostream>
#include <fstream>
#include <vector>
#include <locale>
#include <codecvt>
#include <windows.h>

cv::Mat imreadChinese(const std::string &filename) {
    // 将UTF-8字符串转换为宽字符串
    std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>> converter;
    std::wstring wfilename = converter.from_bytes(filename);

    // 以二进制模式打开文件
    FILE* file = _wfopen(wfilename.c_str(), L"rb");
    if (file == nullptr) {
        return cv::Mat(); // 文件打开失败
    }

    // 获取文件长度
    fseek(file, 0, SEEK_END);
    long filesize = ftell(file);
    fseek(file, 0, SEEK_SET);

    // 读取文件内容到缓冲区
    std::vector<uchar> buf(filesize);
    fread(buf.data(), 1, filesize, file);
    fclose(file);

    // 使用OpenCV的imdecode函数读取图像数据
    cv::Mat img = cv::imdecode(buf, cv::IMREAD_UNCHANGED);
    return img;
}
void writePixelValuesToCSV(const cv::Mat& img, const std::string& csv_filename) {//像素值写入csv文件
    std::ofstream csv_file(csv_filename);

    if (!csv_file.is_open()) {
        std::cerr << "无法创建文件: " << csv_filename << std::endl;
        return;
    }

    if (img.depth() == CV_16U && img.channels() == 1) {
        for (int i = 0; i < img.rows; i++) {
            for (int j = 0; j < img.cols; j++) {
                ushort pixelValue = img.at<ushort>(i, j);
                csv_file << pixelValue;
                if (j != img.cols - 1)
                    csv_file << ",";
            }
            csv_file << "\n";
        }
    } else {
        std::cerr << "不支持的图像类型" << std::endl;
    }

    csv_file.close();
}
void printPixelValues(const cv::Mat& img) {//输出所有点的像素值
    for (int i = 0; i < img.rows; i++) {
        for (int j = 0; j < img.cols; j++) {
            std::cout << "Pixel at (" << i << ", " << j << "): " << static_cast<int>(img.at<ushort>(i, j)) << std::endl;
        }
    }
}
/*
int main() {
    // 使用中文路径
    std::string filename = "E:\\实验数据\\雾化锥角\\20230416\\实验编号81\\44000.tif"; // 确保编码为UTF-8

    cv::Mat img = imreadChinese(filename);
    std::string csv_filename = "output.csv";
    writePixelValuesToCSV(img, csv_filename);

    std::cout << "像素值已保存到 " << csv_filename << std::endl;

    return 0;
}
*/