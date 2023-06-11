import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties

class HistogramFrame(ttk.Frame):
    def __init__(self, master, image):
        super().__init__(master)
        self.master = master
        self.image = image

        self.histogram = self.calculate_histogram()
        self.x_range = self.get_x_range()

        self.create_histogram_plot()

    def calculate_histogram(self):
        hist_range = (0, 256) if self.image.dtype == np.uint8 else (0, 65536)
        histogram = cv2.calcHist([self.image], [0], None, [hist_range[1]], hist_range)
        histogram = histogram.flatten()
        return histogram

    def get_x_range(self):
        x_range = (0, 255) if self.image.dtype == np.uint8 else (0, 65535)
        return x_range

    def create_histogram_plot(self):
        fig = Figure(figsize=(5, 4), dpi=100)
        plot = fig.add_subplot(111)

        font = FontProperties(fname=r'C:\Windows\Fonts\SimHei.ttf', size=12)  # 替换为你的中文字体文件路径
        plot.plot(self.histogram, color='black')
        plot.set_xlabel('灰度值', fontproperties=font)
        plot.set_ylabel('像素点个数', fontproperties=font)
        plot.set_title('灰度值分布图', fontproperties=font)

        plot.set_xlim(self.x_range)

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


# 示例用法
image = cv2.imdecode(np.fromfile(file=r'D:\雾化锥角\44_16000-26000-AverageFigure.tif',dtype=np.uint8),-1)  # 替换为你的图像数组
image=np.array(np.floor(image/(2**8)),dtype='uint8')
root = tk.Tk()
histogram_frame = HistogramFrame(root, image)
histogram_frame.pack()

root.mainloop()
