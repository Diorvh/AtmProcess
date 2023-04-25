import tkinter as tk
from tkinter import ttk
import cv2 as cv
from PIL import ImageTk,Image
import numpy as np
class ClassFigure(ttk.Label):
    def __init__(self,master):
        self.root=master
        super().__init__(self.root)
        #初始化
        self.update_figure(np.random.randint(0,256,size=(300,100),dtype='uint8'))
    def update_figure(self,img,**kwargs):
        self.img=img
        if self.img.dtype==16:
            self.img_show=np.array(np.round(self.img/(2**8)),dtype='uint8')
        else:
            self.img_show=np.array(self.img,dtype='uint8')
        self.img_show=cv.cvtColor(self.img_show,cv.COLOR_GRAY2BGR)
        self.draw_figure(**kwargs)
        self.print_figure()
    def draw_figure(self,**kwargs):
        #补充每个子类的画图方式
        pass
    def print_figure(self):
        self.ImgShow=ImageTk.PhotoImage(Image.fromarray(self.img_show))
        self.configure(image=self.ImgShow)
if __name__=='__main__':
    root=tk.Tk()
    ClassFigure(root).pack()
    root.mainloop()