#include <vector>
using namespace std;
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