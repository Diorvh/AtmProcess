#include <opencv2/opencv.hpp>
#include <string>
#include <iostream>
#include <fstream>
#include <vector>
#include <locale>
#include <codecvt>
#include <windows.h>
using namespace cv;
// 用于绘制线条的函数
void draw_line(cv::Mat &img, int originx, int originy, double angle, Scalar color = Scalar(255, 255, 255), int length = 1000) {
    int x2 = static_cast<int>(originx - length * cos(angle * CV_PI / 180));
    int y2 = static_cast<int>(originy + length * sin(angle * CV_PI / 180));
    cv::line(img, Point(originx, originy), Point(x2, y2), color, 1);
}

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

void saveImageToChinesePath(const cv::Mat& image, const std::string& chinesePath) {
    try {
        // 将中文路径转换为UTF-16编码
        std::wstring widePath;
        widePath.resize(MultiByteToWideChar(CP_UTF8, 0, chinesePath.c_str(), -1, nullptr, 0));
        MultiByteToWideChar(CP_UTF8, 0, chinesePath.c_str(), -1, &widePath[0], static_cast<int>(widePath.size()));

        // 将图像编码为字节流
        std::vector<uchar> imageBuffer;
        cv::imencode(".tif", image, imageBuffer);

        // 使用 Windows API 打开文件
        HANDLE hFile = CreateFileW(
            widePath.c_str(),
            GENERIC_WRITE,
            0,
            nullptr,
            CREATE_ALWAYS,
            FILE_ATTRIBUTE_NORMAL,
            nullptr
        );

        if (hFile == INVALID_HANDLE_VALUE) {
            throw std::runtime_error("无法打开文件：" + chinesePath);
        }

        // 写入字节流到文件
        DWORD bytesWritten;
        WriteFile(hFile, imageBuffer.data(), imageBuffer.size(), &bytesWritten, nullptr);

        // 关闭文件
        CloseHandle(hFile);

        std::wcout << L"图片保存成功：" << widePath << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "保存图片时发生错误：" << e.what() << std::endl;
    }
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