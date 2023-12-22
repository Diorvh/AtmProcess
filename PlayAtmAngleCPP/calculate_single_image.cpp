#define _USE_MATH_DEFINES
#include <vector>
#include <numeric>
#include <cmath>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <iomanip> 
#include "Interpolate2D.cpp"
#include "SG_Filter_1st.cpp"
// #include "libcv.cpp"
using namespace std;
using namespace cv;
pair<pair<vector<double>, vector<double>>,pair<vector<double>, vector<double>>> calculate_grayavg_byangle(
    const Mat & img, int XLeft, int XRight, int Y, int Rmax,
    int ThetaLeft0, int ThetaLeft1, int ThetaRight0, int ThetaRight1,
    int NumAvgL, int RStartL, int NumAvgR, int RStartR) {

    vector<double> resL, anglesL, resR, anglesR;

    // Calculate for left side
    for (int theta = ThetaLeft0; theta >= ThetaLeft1; --theta) {
        double sumGray = 0;
        double sumS = 0;
        double npsin=sin((theta*0.1+0.05)/180*M_PI);
        double npcos=cos((theta*0.1+0.05)/180*M_PI);
        int r = (theta - ThetaLeft1) >= NumAvgL ? 0 : RStartL;//目前只对批量计算生效，单张不能使用，否则单张计算会出问题
        double CenterX=XLeft - (r + 0.5) * npcos;
        double CenterY=Y + (r + 0.5) * npsin;
        while (CenterX >= 0 &&
               CenterY <= img.rows - 1 &&  // 使用 img.rows 和 img.cols
               r <= Rmax) {

            double S = M_PI * (2*r+1) * 0.1 / 360;
            double gray = interpolate2D(img, CenterY, CenterX);
            sumGray += S * gray;
            sumS += S;
            ++r;
            CenterX=XLeft - (r + 0.5) * npcos;
            CenterY=Y + (r + 0.5) * npsin;
        }
        if (sumS != 0) {
            resL.push_back(sumGray / sumS);
            anglesL.push_back(theta * 0.1 + 0.05);
        }
    }

    // Calculate for right side
    for (int theta = ThetaRight0; theta < ThetaRight1; ++theta) {
        double sumGray = 0;
        double sumS = 0;
        double npsin=sin((theta*0.1+0.05)/180*M_PI);
        double npcos=cos((theta*0.1+0.05)/180*M_PI);
        int r = -(theta-ThetaRight1) >= NumAvgR ? 0 : RStartR;//目前只对批量计算生效，单张不能使用，否则单张计算会出问题
        double CenterX=XRight - (r + 0.5) * npcos;
        double CenterY=Y + (r + 0.5) * npsin;

        while (CenterX <= img.cols-1 && CenterY <= img.rows - 1 && r <= Rmax) {

            double S = M_PI * (2*r+1) * 0.1 / 360;
            double gray = interpolate2D(img, CenterY, CenterX);
            sumGray += S * gray;
            sumS += S;
            ++r;
            CenterX=XRight - (r + 0.5) * npcos;
            CenterY=Y + (r + 0.5) * npsin;
        }

        if (sumS != 0) {
            resR.push_back(sumGray / sumS);
            anglesR.push_back(theta * 0.1 + 0.05);
        }
    }
    // cout<<anglesL.size()<<' '<<anglesR.size()<<endl;
    return { {anglesL, resL}, {anglesR, resR} };
}
double calculateThreshold(const vector<double>& data, int numAvg, double thresRatio) {
    double cache_max = accumulate(data.begin(), data.begin() + numAvg, 0.0) / numAvg;
    double cache_min = accumulate(data.end() - numAvg, data.end(), 0.0) / numAvg;
    return cache_min + (cache_max - cache_min) * thresRatio;
}

int findLastGreaterEqual(const vector<double>& arr, double thres) {
    for (int i = arr.size() - 1; i >= 0; --i) {
        if (arr[i] >= thres) return i;
    }
    return -1;
}

pair<double, double> calculateAtmAngleThresP2(const vector<double>& resLAngles, 
                                                   const vector<double>& resLValues,
                                                   const vector<double>& resRAngles, 
                                                   const vector<double>& resRValues,
                                                   int numAvgL, int numAvgR, 
                                                   double thresRatioL, double thresRatioR,
                                                   int window_length, int polyorder) {
    double thresL = calculateThreshold(resLValues, numAvgL, thresRatioL);
    double thresR = calculateThreshold(resRValues, numAvgR, thresRatioR);

    vector<double> filteredL =savitzkyGolayFilter_1st(resLValues,window_length);
    vector<double> filteredR =savitzkyGolayFilter_1st(resRValues,window_length);

    int angleLPos = findLastGreaterEqual(filteredL, thresL);
    int angleRPos = findLastGreaterEqual(filteredR, thresR);
    //输出excel文档
    // ofstream file("output.csv");
    // file<<fixed<<setprecision(2);
    // for (size_t i=0;i<resLAngles.size();++i){
    //     file<<resLAngles[i]<<','<<filteredL[i]<<','<<resRAngles[i]<<','<<filteredR[i]<<'\n';
    // }
    // file.close();
    return {resLAngles[angleLPos], resRAngles[angleRPos]};
}
pair<double,double> calculate_atm_angle_thres(const Mat& img, int XLeft, int XRight, int Y, int Rmax,
                                                int ThetaLeft, int ThetaRight,
                                                int NumAvgL, int RStartL, int NumAvgR, int RStartR,
                                                double thresRatioL, double thresRatioR,int window_length, int polyorder){
    auto res=calculate_grayavg_byangle(img,XLeft,XRight,Y,Rmax,899,ThetaLeft,900,ThetaRight,NumAvgL,RStartL,NumAvgR,RStartR);
    return calculateAtmAngleThresP2(res.first.first,res.first.second,res.second.first,res.second.second,NumAvgL,NumAvgR,thresRatioL,thresRatioR,window_length,polyorder);
}
/*
int main(){
    string dir="E:\\实验数据\\雾化锥角\\20230416\\实验编号81\\";
    clock_t start_time=clock();//计时
    Mat img;
    for (int i=44000;i<=44100;++i){
        img=65535-imreadChinese(dir+to_string(i)+".tif");
        pair<double,double> res=calculate_atm_angle_thres(img,275,302,114,400,0,1800,100,0,100,0,0.5,0.4,50,1);
        cout<<res.first<<' '<<res.second<<endl;
    }
    std:: cout << "The run time is: " <<(double)(clock() - start_time) / CLOCKS_PER_SEC << "s" << std::endl;//计时
    return 0;
}*/