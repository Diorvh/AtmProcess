import numpy as np


def interpolate1D(x, x1, y1, x2, y2):
    if x1 == x2:
        return y1
    return (x2 - x) / (x2 - x1) * y1 + (x - x1) / (x2 - x1) * y2


def interpolate2D(data, x, y):
    x1 = int(np.floor(x))
    x2 = min(int(x) + 1, data.shape[0] - 1)
    y1 = int(np.floor(y))
    y2 = min(int(y) + 1, data.shape[1] - 1)
    z1 = interpolate1D(x, x1, data[x1][y1], x2, data[x2][y1])
    z2 = interpolate1D(x, x1, data[x1][y2], x2, data[x2][y2])
    return interpolate1D(y, y1, z1, y2, z2)
