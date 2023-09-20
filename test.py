import numpy as np
from scipy.interpolate import griddata

# 已知四个点的坐标和对应的函数值
points = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
values = np.array([0, 1, 3, 5])  # 替换f(x, y)为相应的函数值

# 定义要进行插值的网格坐标
x_grid, y_grid = np.meshgrid(0.5, 0.5)

# 使用griddata进行线性插值
interpolated_values = griddata(points, values, (x_grid, y_grid), method='linear')
print(interpolated_values)
# interpolated_values 包含了网格上的线性插值结果
