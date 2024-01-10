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
#include "lib_file.cpp"
#include "lib_algorithm.cpp"
#include "calculate_single_image.cpp"
using namespace std;
namespace fs = std::filesystem;
// 线程函数

pair<vector<double>,vector<double>> process_calculate_atmangle(string dirr, vector<int> NAME, int XLeft, int XRight, int Y, int Rmax, int ThetaLeft, int ThetaRight,
                                int NumAvgL, int RStartL, int NumAvgR, int RStartR,
                                double ThresRatioL, double ThresRatioR, int windows_length, int polyorder, int FlagSaveImg) {
    // 定义结果向量
    vector<double> resL, resR;

    for (int j=0;j<NAME.size();++j) {
        int i=NAME[j];
        if (i % 100 == 0) {
            cout << "Processing:" <<i<<"("<< j*100.0/NAME.size()<<"%)"<<endl;
        }

        string filepath = dirr + "/" + to_string(i) + ".tif";
        cv::Mat img = imreadChinese(filepath),rev_img;
        bitwise_not(img,rev_img);
        auto res = calculate_atm_angle_thres(rev_img, XLeft, XRight, Y, Rmax, ThetaLeft, ThetaRight, NumAvgL, RStartL, NumAvgR, RStartR, ThresRatioL, ThresRatioR, windows_length, polyorder);
        resL.push_back(res.first);
        resR.push_back(res.second);
        if (FlagSaveImg) {
            //TODO: 检测一下8bit的归一化前后是不是一致的
            cv::normalize(img, img, 0, 255, cv::NORM_MINMAX, CV_8U);
            if (img.channels() == 1)
                cvtColor(img, img, COLOR_GRAY2RGB);
            int MAX = 255;
            ellipse(img, Point(XLeft, Y), Size(Rmax, Rmax), 0, 90, 180 - ThetaLeft * 0.1, Scalar(MAX, 0, 0), 1);
            ellipse(img, Point(XRight, Y), Size(Rmax, Rmax), 0, 180 - ThetaRight * 0.1, 90, Scalar(MAX, 0, 0), 1);
            draw_line(img, XLeft, Y, res.first, Scalar(0, 0, MAX));
            draw_line(img, XRight, Y, res.second, Scalar(0, 0, MAX));

            string result_dir = dirr + "/处理结果";
            // createFolder(result_dir);
            string savepath=result_dir + "/" + to_string(i) + ".tif";
            saveImageToChinesePath(img,savepath);
        }
    }
    return {resL, resR};
}

void updateFile(const std::string& filePath, const std::string& newStr) {//删掉最后一行及空行，然后替换为newStr
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

int main() {
    //读取
    char buffer[MAX_PATH];
    GetModuleFileNameA(NULL, buffer, MAX_PATH);
    string wkdir(buffer);
    wkdir=getFolderPath(wkdir);
    // cout<<wkdir<<endl;
    ifstream file(wkdir+"//inputcpp.txt");
    if (!file.is_open()) {
        cerr << "Failed to open file\n";
        return 1;
    }
    string dirr;
    int START, END, Decimate, num_processes;
    int XLeft, XRight, Y, Rmax, ThetaLeft, ThetaRight, NumAvgL, RStartL, NumAvgR, RStartR;
    double ThresRatioL, ThresRatioR;
    int window_length, polyorder, FlagSaveImg, Mode;//window_length必须为奇数，否则会与python计算结果不一致。理论上确实也只应该是奇数
    getline(file, dirr);
    file >> START >> END >> Decimate >> num_processes;
    file >> XLeft >> XRight >> Y >> Rmax >> ThetaLeft >> ThetaRight >> NumAvgL >> RStartL >> NumAvgR >> RStartR;
    file >> ThresRatioL >> ThresRatioR;
    file >> window_length >> polyorder >> FlagSaveImg >> Mode;
    file.close();
    //计时
    clock_t start_time=clock();
    if (Mode==1){
        // 创建任务分配
        vector<vector<int>> chunks(num_processes);
        int chunk_size = (END - START + 1) / num_processes/Decimate;
        for (int i = 0; i < num_processes; ++i) {
            int chunk_start = START + i * chunk_size*Decimate;
            int chunk_end = (i == num_processes - 1) ? END : chunk_start + chunk_size*Decimate - 1;
            for (int j = chunk_start; j <= chunk_end; j+=Decimate) {
                chunks[i].push_back(j);
            }
        }
        // for (auto element:chunks){
        //     for (auto element2:element){
        //         cout<<element2<<',';
        //     }
        //     cout<<endl;
        // }
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
            fileo<<(i*Decimate+START)<<','<<resL[i]<<','<<resR[i]<<','<<resR[i]-resL[i]<<'\n';
        }
        fileo.close();

        updateFile(wkdir+"//inputpy.txt",extractLastPathComponent(dirr));

        string command="python "+wkdir+"//process_cpp_result.py";
        system(command.c_str());        
    }
    else {//只处理单张，因为要显示曲线，所以只能用python原生计算了，这里先预留
        0;//process_calculate_atmangle(ref(dirr), vector<int>(START), XLeft, XRight, Y, Rmax, ThetaLeft, ThetaRight, NumAvgL, RStartL, NumAvgR, RStartR, ThresRatioL, ThresRatioR, window_length, polyorder, 1);
    }
    return 0;
}