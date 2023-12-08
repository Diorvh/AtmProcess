#include <vector>
#include <cmath>
#include <algorithm>

using namespace std;

// Assuming interpolate2D is already defined
double interpolate2D(const vector<vector<double>>& img, double x, double y);

pair<vector<double>, vector<double>> calculate_grayavg_byangle(
    const vector<vector<double>>& img, int XLeft, int XRight, int Y, int Rmax,
    int ThetaLeft, int ThetaRight,
    int NumAvgL, int RStartL, int NumAvgR, int RStartR,
    const vector<double>& npcos, const vector<double>& npsin) {

    vector<double> resL, anglesL, resR, anglesR;

    // Calculate for left side
    for (int theta = 899; theta >= ThetaLeft; --theta) {
        double sumGray = 0;
        double sumS = 0;
        double npsin=sin(theta*0.1+0.05);
        double npcos=cos(theta*0.1+0.05);
        int r = (theta - ThetaLeft) >= NumAvgL ? 0 : RStartL;
        double CenterX=XLeft - (r + 0.5) * npcos;
        double CenterY=Y + (r + 0.5) * npsin;
        while (CenterX >= 0 &&
               CenterY <= static_cast<int>(img.size()) - 1 &&
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
    for (int theta = 900; theta < ThetaRight; ++theta) {
        double sumGray = 0;
        double sumS = 0;
        double npsin=sin(theta*0.1+0.05);
        double npcos=cos(theta*0.1+0.05);
        int r = -(theta-ThetaRight) >= NumAvgR ? 0 : RStartR;
        double CenterX=XRight - (r + 0.5) * npcos;
        double CenterY=Y + (r + 0.5) * npsin;

        while (CenterX < static_cast<int>(img[0].size()) && CenterY <= static_cast<int>(img.size()) - 1 && r <= Rmax) {

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

    return { {anglesL, resL}, {anglesR, resR} };
}
