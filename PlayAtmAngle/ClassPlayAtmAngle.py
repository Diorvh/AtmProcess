import tkinter as tk
from tkinter import ttk
import cv2 as cv
from lib.lib_tkwidget import *
from lib.ClassFigure import *
from lib.BaseClass import *
from lib.Table import *
from PlayAtmAngle.PlayAtmAngle import *
import time
class ClassFigurePlayAtmAngle(ClassFigure):#改名
    def __init__(self,father):#back为本文件前端Class的back
        super().__init__(father)
    def draw_figure(self, **kwargs):
        super().draw_figure(**kwargs)
        if self.back.FlagReverseColor:
            self.img_show=255-self.img_show
    def generate_FilenameSave(self):#每个类要重写
        return str(self.back.root.Main.generate_ImageLabel())+'-'+str(self.back.root.Main.FrameChoosePic.FigName)+'-AtmAngle.tif'
class ClassPlayAtmAngle(BaseFrame):#改名
    def __init__(self,father):
        self.father=father
        self.db=father.db
        self.back=self.father.back.PlayAtmAngle#改名
        super().__init__(self.father,padding=5,relief='sunken')
        self.FramePanel=ttk.Frame(self)
        self.FramePanel.grid(row=0,column=0)
        self.create_panel()
        self.Figure=ClassFigurePlus(self,ClassFigurePlayAtmAngle)#改名
        self.back.Figure=self.Figure
        self.Figure.grid(row=1,column=0)
        #以上为默认，不要动，以下可添加图片绑定功能self.Figure.Figure.bind('<Key>',self.CommandBindFigureKey)
    def create_panel(self):
        #R1
        self.FrameR1=ttk.Frame(self.FramePanel)
        self.FrameR1.pack(side='left')
        self.create_var('FlagReverseColor',self.back,'Boolean',False,True)
        ttk.Button(self.FrameR1,text='颜色翻转',command=self.CommandButtonReverseColor).pack(side='left')
        # self.create_var('FigStart',self.back,'Int',0,True)
        # self.create_var('FigEnd',self.back,'Int',0,True)
        # self.LER1_1=LabelEntry(self.FrameR1,'起始帧：',self.FigStart)
        # self.LER1_1.pack(side='left')
        # self.LER1_1.entry.bind('<Return>',self.CommandBindFigStart)
        # self.LER1_2=LabelEntry(self.FrameR1,'结束帧：',self.FigEnd)
        # self.LER1_2.pack(side='left')
        # self.LER1_2.entry.bind('<Return>',self.CommandBindFigEnd)
        # ttk.Button(self.FramePanel,text='计算平均图',command=self.CommandButtonCalcAverage).pack(side='left')
    # def CommandBindFigStart(self,event):
    #     self.back.update('FigStart',self.FigStart.get(),False)
    # def CommandBindFigEnd(self,event):
    #     self.back.update('FigEnd',self.FigEnd.get(),False)
    def CommandButtonReverseColor(self):
        self.back.update('FlagReverseColor',not self.FlagReverseColor.get())
        self.FreshSelf()
    # def CommandButtonCalcAverage(self):
    #     start_time=time.time()
    #     print('计算平均图中')
    #     self.FreshSelf(calculate_average_image(self.back.root.Main.generate_fdir(),self.FigStart.get(),self.FigEnd.get(),self.back.root.Main.CoreNum))
    #     print('计算完成，耗时',time.time()-start_time,'秒')

    def FreshSelf(self):
        img=cv.imdecode(np.fromfile(file=self.back.root.Main.FrameChoosePic.get_dir_tif(),dtype=np.uint8),-1)
        self.Figure.Figure.change_figure(img)
        self.back.Fresh()