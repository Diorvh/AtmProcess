#include <opencv2/opencv.hpp>
#include <iostream>
#include <string>
#include "libcv.cpp"
#include "lib_file.cpp"

using namespace cv;
using namespace std;

Mat process_trans_and_add_img(string dirr, vector<int> NAME) {
    cv::Mat res=imreadChinese(dirr + "/" + to_string(NAME.front()) + ".tif");
    res.setTo(0.0);
    for (int i=NAME.front();i<=NAME.back();++i) {
        if (i % 100 == 0) {
            cout << "Processing:" <<i<<"("<< (i-NAME.front())*100.0/NAME.size()<<"%)"<<endl;
        }
        string filepath = dirr + "/" + to_string(i) + ".tif";
        cout<<filepath<<endl;
        cv::Mat img = imreadChinese(filepath);
        // 转换为黑白图片
        Mat grayscaleImage;
        cv::normalize(img, img, 0, 65535, cv::NORM_MINMAX, CV_16U);
        cvtColor(img, grayscaleImage, COLOR_BGR2GRAY);
        // 保存黑白图片
        saveImageToChinesePath(grayscaleImage,filepath);
        // 累积图像用于计算平均值
        grayscaleImage.convertTo(grayscaleImage, CV_64F);
        res += grayscaleImage;
    }
    return res;
}
int main() {
    // 输入参数
    char buffer[MAX_PATH];
    GetModuleFileNameA(NULL, buffer, MAX_PATH);
    string wkdir(buffer);
    wkdir=getFolderPath(wkdir);
    // cout<<wkdir<<endl;
    ifstream file(wkdir+"//inputcppprocess.txt");
    if (!file.is_open()) {
        cerr << "Failed to open file\n";
        return 1;
    }
    string dirr;
    int START, END;
    getline(file, dirr);
    file >> START >> END;
    file.close();
    vector<int> input={START,END};
    // 调用函数进行图片处理和保存
    Mat ans=process_trans_and_add_img(dirr, input);
    ans=ans/(END-START+1);
    // 构建平均图像的输出文件名
    string averageOutputFileName = dirr+"_"+to_string(START)+"-"+to_string(END)+"_AverageFigure.tif";

    // 保存平均图像
    ans.convertTo(ans, CV_8U);
    saveImageToChinesePath(ans, averageOutputFileName);

    return 0;
}


