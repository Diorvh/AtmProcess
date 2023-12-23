#define _USE_MATH_DEFINES
#include <opencv2/opencv.hpp>
#include <thread>
#include <vector>
#include <iostream>
#include <fstream>
#include <filesystem>
#include <future>
#include <iomanip>
#include <numeric>
#include <cmath>
#include <cstdlib>
#include <Windows.h>
#include "libcv.cpp"
#include "calculate_single_image.cpp"
using namespace std;
namespace fs = std::filesystem;
// 用于绘制线条的函数
void draw_line(cv::Mat &img, int originx, int originy, double angle, Scalar color = Scalar(255, 255, 255), int length = 1000) {
    int x2 = static_cast<int>(originx - length * cos(angle * CV_PI / 180));
    int y2 = static_cast<int>(originy + length * sin(angle * CV_PI / 180));
    cv::line(img, Point(originx, originy), Point(x2, y2), color, 1);
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

void createFolder(const std::string& chineseFolderPath) {
    try {
        // Convert Chinese path to UTF-16 encoding
        std::wstring wideFolderPath;
        wideFolderPath.resize(MultiByteToWideChar(CP_UTF8, 0, chineseFolderPath.c_str(), -1, nullptr, 0));
        MultiByteToWideChar(CP_UTF8, 0, chineseFolderPath.c_str(), -1, &wideFolderPath[0], static_cast<int>(wideFolderPath.size()));

        // Check if the folder exists
        if (GetFileAttributesW(wideFolderPath.c_str()) == INVALID_FILE_ATTRIBUTES) {
            // If the folder doesn't exist, create it
            if (!CreateDirectoryW(wideFolderPath.c_str(), NULL)) {
                throw std::runtime_error("Error creating folder: " + std::to_string(GetLastError()));
            }
            std::wcout << L"Folder created successfully: " << wideFolderPath << std::endl;
        }
        else {
            std::wcout << L"Folder already exists: " << wideFolderPath << std::endl;
        }
    } catch (const std::exception& e) {
        std::cerr << "Error creating folder: " << e.what() << std::endl;
    }
}

// 线程函数

pair<vector<double>,vector<double>> process_calculate_atmangle(string dirr, vector<int> NAME, int XLeft, int XRight, int Y, int Rmax, int ThetaLeft, int ThetaRight,
                                int NumAvgL, int RStartL, int NumAvgR, int RStartR,
                                double ThresRatioL, double ThresRatioR, int windows_length, int polyorder, int FlagSaveImg) {
    // 定义结果向量
    vector<double> resL, resR;

    for (int i=NAME.front();i<=NAME.back();++i) {
        if (i % 100 == 0) {
            cout << "Processing:" <<i<<"("<< (i-NAME.front())*100.0/NAME.size()<<"%)"<<endl;
        }

        string filepath = dirr + "/" + to_string(i) + ".tif";
        cv::Mat img = imreadChinese(filepath);

        auto res = calculate_atm_angle_thres(65535-img, XLeft, XRight, Y, Rmax, ThetaLeft, ThetaRight, NumAvgL, RStartL, NumAvgR, RStartR, ThresRatioL, ThresRatioR, windows_length, polyorder);
        resL.push_back(res.first);
        resR.push_back(res.second);
        if (FlagSaveImg) {
            cv::normalize(img, img, 0, 255, cv::NORM_MINMAX, CV_8U);
            if (img.channels() == 1) {
                cvtColor(img, img, COLOR_GRAY2RGB);
            }
            int MAX = 255;
            ellipse(img, Point(XLeft, Y), Size(Rmax, Rmax), 0, 90, 180 - ThetaLeft * 0.1, Scalar(MAX, 0, 0), 1);
            ellipse(img, Point(XRight, Y), Size(Rmax, Rmax), 0, 180 - ThetaRight * 0.1, 90, Scalar(MAX, 0, 0), 1);
            draw_line(img, XLeft, Y, res.first, Scalar(0, 0, MAX));
            draw_line(img, XRight, Y, res.second, Scalar(0, 0, MAX));

            string result_dir = dirr + "/处理结果";
            createFolder(result_dir);
            string savepath=result_dir + "/" + to_string(i) + ".tif";
            saveImageToChinesePath(img,savepath);
        }
    }
    return {resL, resR};
}
double calculateAverage(const vector<double>& vec) {
    if (vec.empty()) {
        return 0.0; // 避免除以零
    }

    double sum = accumulate(vec.begin(), vec.end(), 0.0);
    double average = sum / vec.size();

    return average;
}
double calculateStandardDeviation(const vector<double>& vec) {
    if (vec.size() <= 1) {
        return 0.0; // 样本大小小于等于 1 时标准差为 0
    }

    double sum = accumulate(vec.begin(), vec.end(), 0.0);
    double mean = sum / vec.size();

    double sq_sum = inner_product(vec.begin(), vec.end(), vec.begin(), 0.0,
        [](double sum, double val) { return sum + val; },
        [mean](double val1, double val2) { return (val1 - mean) * (val2 - mean); });

    double variance = sq_sum / (vec.size() - 1);
    return sqrt(variance);
}
vector<double> subtractVectors(const vector<double>& vec1, const vector<double>& vec2) {

    vector<double> result(vec1.size());
    for (size_t i = 0; i < vec1.size(); ++i) {
        result[i] = vec1[i] - vec2[i];
    }

    return result;
}

void updateFile(const std::string& filePath, const std::string& newStr) {
    // Open the file in read mode to read its contents
    std::ifstream inFile(filePath);
    if (!inFile.is_open()) {
        std::cerr << "Error opening file: " << filePath << std::endl;
        return;
    }

    // Read all lines from the file and store them in a vector
    std::vector<std::string> lines;
    std::string line;
    while (std::getline(inFile, line)) {
        lines.push_back(line);
    }

    // Close the input file
    inFile.close();

    // Remove trailing empty lines
    while (!lines.empty() && lines.back().empty()) {
        lines.pop_back();
    }

    // Remove the last line
    if (!lines.empty()) {
        lines.pop_back();
    }

    // Add the new string as the last line
    lines.push_back(newStr);

    // Open the file in write mode to update its contents
    std::ofstream outFile(filePath);
    if (!outFile.is_open()) {
        std::cerr << "Error opening file for writing: " << filePath << std::endl;
        return;
    }

    // Write the modified lines back to the file
    for (const auto& updatedLine : lines) {
        outFile << updatedLine << std::endl;
    }

    // Close the output file
    outFile.close();
}

std::string extractLastPathComponent(const std::string& path) {//读入一个文件路径字符串，只保留最后一个//后的内容
    // Find the last occurrence of '\\' in the path
    size_t lastBackslashPos = path.find_last_of("//");

    // Check if the character was found
    if (lastBackslashPos != std::string::npos) {
        // Extract the substring after the last '\\' character
        return path.substr(lastBackslashPos + 1);
    } else {
        // If '\\' is not found, return the entire string
        return path;
    }
}
std::string getFolderPath(const std::string& filePath) {
    // 使用C++17中引入的std::filesystem
    std::filesystem::path fullPath(filePath);

    // 获取文件所在文件夹的路径
    std::filesystem::path folderPath = fullPath.parent_path();

    // 将路径转换为字符串
    std::string folderPathString = folderPath.string();

    return folderPathString;
}

int main() {
    //读取
    char buffer[MAX_PATH];
    GetModuleFileNameA(NULL, buffer, MAX_PATH);
    string wkdir(buffer);
    wkdir=getFolderPath(wkdir);
    cout<<wkdir<<endl;
    ifstream file(wkdir+"//inputcpp.txt");
    if (!file.is_open()) {
        cerr << "Failed to open file\n";
        return 1;
    }
    string dirr;
    int START, END, num_processes;
    int XLeft, XRight, Y, Rmax, ThetaLeft, ThetaRight, NumAvgL, RStartL, NumAvgR, RStartR;
    double ThresRatioL, ThresRatioR;
    int window_length, polyorder, FlagSaveImg;//window_length必须为奇数，否则会与python计算结果不一致。理论上确实也只应该是奇数
    getline(file, dirr);
    file >> START >> END >> num_processes;
    file >> XLeft >> XRight >> Y >> Rmax >> ThetaLeft >> ThetaRight >> NumAvgL >> RStartL >> NumAvgR >> RStartR;
    file >> ThresRatioL >> ThresRatioR;
    file >> window_length >> polyorder >> FlagSaveImg;
    file.close();
    //计时
    clock_t start_time=clock();
    // 创建任务分配
    vector<vector<int>> chunks(num_processes);
    int chunk_size = (END - START + 1) / num_processes;
    for (int i = 0; i < num_processes; ++i) {
        int chunk_start = START + i * chunk_size;
        int chunk_end = (i == num_processes - 1) ? END : chunk_start + chunk_size - 1;
        for (int j = chunk_start; j <= chunk_end; ++j) {
            chunks[i].push_back(j);
        }
    }
    createFolder(dirr + "/处理结果");

    // 创建并启动异步任务
    vector<future<pair<vector<double>,vector<double>>>> futures;
    for (int i = 0; i < num_processes; ++i) {
        futures.push_back(async(launch::async, process_calculate_atmangle, ref(dirr), ref(chunks[i]), XLeft, XRight, Y, Rmax, ThetaLeft, ThetaRight, NumAvgL, RStartL, NumAvgR, RStartR, ThresRatioL, ThresRatioR, window_length, polyorder, FlagSaveImg));
    }

    // 收集结果
    vector<double> resL,resR;
    for (auto &f : futures) {
        pair<vector<double>, vector<double>> result = f.get(); // Wait for the task to complete and get the result
        resL.insert(resL.end(), result.first.begin(), result.first.end());
        resR.insert(resR.end(), result.second.begin(), result.second.end());
    }
    double compute_time=(double)(clock() - start_time) / CLOCKS_PER_SEC;
    cout << "The run time is: " <<compute_time << "s" << endl;//计时
    //输出结果

    ofstream fileo(wkdir+"/result.csv");

    fileo << fixed << setprecision(3);
    fileo << "XLeft,XRight,Y,Rmax,ThetaLeft,ThetaRight,window_length,polyorder,NumAvgL,NumAvgR,ThresRatioL,ThresRatioR,num_processes,compute_time" << endl;
    
    fileo<<XLeft<<','<<XRight<<','<<Y<<','<<Rmax<<','<<ThetaLeft<<','<<ThetaRight<<','<<window_length<<','<<polyorder<<','<<NumAvgL<<','<<NumAvgR<<','<<ThresRatioL<<','<<ThresRatioR<<','<<num_processes<<','<<compute_time<<endl;
    fileo<<fixed<<setprecision(6);
    fileo<<"Frame,AngleL,AngleR,AtmAngle"<<endl;
    fileo<<"Average,"<<calculateAverage(resL)<<','<<calculateAverage(resR)<<','<<calculateAverage(resR)-calculateAverage(resL)<<endl;
    fileo<<"StDev,"<<calculateStandardDeviation(resL)<<','<<calculateStandardDeviation(resR)<<','<<calculateStandardDeviation(subtractVectors(resR,resL))<<endl;
    fileo<<"RelativeStDev,"<<calculateStandardDeviation(resL)/(calculateAverage(resR)-calculateAverage(resL))<<','<<calculateStandardDeviation(resR)/(calculateAverage(resR)-calculateAverage(resL))<<','<<calculateStandardDeviation(subtractVectors(resR,resL))/(calculateAverage(resR)-calculateAverage(resL))<<endl;
    for (int i=0;i<resL.size();++i){
        fileo<<(i+START)<<','<<resL[i]<<','<<resR[i]<<','<<resR[i]-resL[i]<<'\n';
    }
    fileo.close();

    updateFile(wkdir+"//inputpy.txt",extractLastPathComponent(dirr));

    string command="python "+wkdir+"//process_cpp_result.py";
    system(command.c_str());

    return 0;
}