import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import PickEvent

FONTSIZE=16
class PlotFrame(ttk.Frame):
    def __init__(self, parent, X=[0], Y=[0], X_name='横轴', Y_name='纵轴'):
        super().__init__(parent)
        self.X = X
        self.Y = Y
        self.X_name=X_name
        self.Y_name=Y_name
        self.create_plot()
        self.create_status_label()

    def create_plot(self):
        self.fig, self.ax = plt.subplots()

        # 绘制图像
        self.line, = self.ax.plot(self.X, self.Y)

        # 设置坐标轴标签为中文
        self.ax.set_xlabel(self.X_name, fontproperties='SimHei', fontsize=FONTSIZE)
        self.ax.set_ylabel(self.Y_name, fontproperties='SimHei', fontsize=FONTSIZE)

        # 创建画布，并将图像显示在画布上
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        # 连接鼠标移动事件
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

    def create_status_label(self):
        self.status_label = ttk.Label(self, text='', font=('SimHei', FONTSIZE))
        self.status_label.pack()

    def update_data(self, new_X, new_Y):#名字设置似乎无效
        # 更新数据
        self.X = new_X
        self.Y = new_Y

        # 清空原有图像
        self.ax.cla()

        # 绘制新图像
        self.line, = self.ax.plot(self.X, self.Y)

        # 重新设置坐标轴标签为中文
        self.ax.set_xlabel(self.X_name, fontproperties='SimHei', fontsize=FONTSIZE)
        self.ax.set_ylabel(self.Y_name, fontproperties='SimHei', fontsize=FONTSIZE)

        # 更新画布
        self.canvas.draw()

    def on_mouse_move(self, event):
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            index = np.abs(self.X - x).argmin()  # 找到最接近的X值对应的索引
            if 0 <= index < len(self.X):
                x_val, y_val = self.X[index], self.Y[index]
                self.status_label.config(text=f'X: {x_val:.2f}, Y: {y_val:.2f}')


# 示例用法
if __name__ == '__main__':
    # 创建主窗口
    root = tk.Tk()
    root.geometry('400x400')

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
