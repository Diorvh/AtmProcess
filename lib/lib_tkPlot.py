import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class PlotFrame(ttk.Frame):
    def __init__(self, parent, X, Y):
        super().__init__(parent)
        self.X = X
        self.Y = Y
        self.create_plot()

    def create_plot(self):
        self.fig, self.ax = plt.subplots()

        # 绘制图像
        self.line, = self.ax.plot(self.X, self.Y)

        # 设置坐标轴标签为中文
        self.ax.set_xlabel('横轴', fontproperties='SimHei', fontsize=12)
        self.ax.set_ylabel('纵轴', fontproperties='SimHei', fontsize=12)

        # 创建画布，并将图像显示在画布上
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

    def update_data(self, new_X, new_Y):
        # 更新数据
        self.X = new_X
        self.Y = new_Y

        # 清空原有图像
        self.ax.cla()

        # 绘制新图像
        self.line, = self.ax.plot(self.X, self.Y)

        # 重新设置坐标轴标签为中文
        self.ax.set_xlabel('横轴', fontproperties='SimHei', fontsize=12)
        self.ax.set_ylabel('纵轴', fontproperties='SimHei', fontsize=12)

        # 更新画布
        self.canvas.draw()


# 示例用法
if __name__ == '__main__':
    # 创建主窗口
    root = tk.Tk()

    # 创建测试数据
    X = np.linspace(0, 10, 100)
    Y = np.sin(X)

    # 创建自定义的图像绘制框架
    plot_frame = PlotFrame(root, X, Y)
    plot_frame.pack(expand=True, fill='both')

    # 模拟数据更新
    def update_data():
        new_X = np.linspace(0, 10, 100)
        new_Y = np.cos(new_X)
        plot_frame.update_data(new_X, new_Y)

    # 创建更新按钮
    update_button = ttk.Button(root, text='更新数据', command=update_data)
    update_button.pack()

    # 运行主循环
    root.mainloop()
