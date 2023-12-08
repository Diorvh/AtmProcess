#include <algorithm>
#include <vector>
#include <cmath>
using namespace std;
double interpolate1D(double x, double x1, double y1, double x2, double y2) {
    if (x1 == x2) {
        return y1;
    } else {
        return (x2 - x) / (x2 - x1) * y1 + (x - x1) / (x2 - x1) * y2;
    }
}
double interpolate2D(const vector<vector<double>>& data, double x, double y) {
    int x1 = static_cast<int>(std::floor(x));
    int x2 = min(static_cast<int>(x) + 1, static_cast<int>(data.size()) - 1);
    int y1 = static_cast<int>(std::floor(y));
    int y2 = min(static_cast<int>(y) + 1, static_cast<int>(data[0].size()) - 1);

    double z1 = interpolate1D(x, x1, data[x1][y1], x2, data[x2][y1]);
    double z2 = interpolate1D(x, x1, data[x1][y2], x2, data[x2][y2]);

    return interpolate1D(y, y1, z1, y2, z2);
}
