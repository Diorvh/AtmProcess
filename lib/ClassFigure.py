import tkinter as tk
from tkinter import ttk
import cv2 as cv
from PIL import ImageTk,Image
import numpy as np
from lib.BaseClass import *
class ClassFigure(ttk.Label):
    def __init__(self,father):
        self.father=father
        self.back=self.father.father.back
        super().__init__(self.father,takefocus=True)
        #初始化
        self.change_figure(np.random.randint(0,256,size=(640,704),dtype='uint8'))
    def change_figure(self,img,**kwargs):
        self.img=img
        if self.img.dtype==16:
            self.img_show=np.array(np.round(self.img/(2**8)),dtype='uint8')
        else:
            self.img_show=np.array(self.img,dtype='uint8')
        if len(self.img.shape)==2:
            self.img_show=cv.cvtColor(self.img_show,cv.COLOR_GRAY2BGR)
        self.update_figure(**kwargs)
    def update_figure(self,**kwargs):
        self.draw_figure(**kwargs)
        self.print_figure()
    def draw_figure(self,**kwargs):
        #补充每个子类的画图方式
        pass
    def print_figure(self):
        self.ImgShow=ImageTk.PhotoImage(Image.fromarray(self.img_show))
        self.configure(image=self.ImgShow)
class ClassFigurePlus(BaseFrame):
    def __init__(self,father,Figure):#Figure为类名
        self.father=father
        super().__init__(self.father)
        self.Figure=Figure(self)
        self.Figure.bind('<Motion>',self.MouseMotion)
        self.FrameParam=ttk.Frame(self)
        self.FrameParam.pack()
        self.Figure.pack()
        self.create_FrameParam()
    def create_FrameParam(self):
        self.MouseX=tk.IntVar(self)
        self.MouseY=tk.IntVar(self)
        self.Gray=tk.IntVar(self)
        ttk.Label(self.FrameParam,text='X:').pack(side='left')
        ttk.Label(self.FrameParam,textvariable=self.MouseX,width=4).pack(side='left')
        ttk.Label(self.FrameParam,text='Y:').pack(side='left')
        ttk.Label(self.FrameParam,textvariable=self.MouseY,width=4).pack(side='left')
        ttk.Label(self.FrameParam,text='灰度值:').pack(side='left')
        ttk.Label(self.FrameParam,textvariable=self.Gray,width=10).pack(side='left')
        ttk.Button(self.FrameParam,text='focus_set（使用小键盘快捷键请先点击此处）',command=self.Figure.focus_set).pack(side='left')
    def MouseMotion(self,event):
        if event.x<self.Figure.img.shape[1]:
            self.MouseX.set(event.x)
        if event.y<self.Figure.img.shape[0]:
            self.MouseY.set(event.y)
        self.Gray.set(self.Figure.img[self.MouseY.get(),self.MouseX.get()])
if __name__=='__main__':
    root=tk.Tk()
    ClassFigure(root).pack()
    root.mainloop()