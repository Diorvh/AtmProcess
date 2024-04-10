import tkinter as tk
from tkinter import ttk
import cv2 as cv
from lib.lib_tkwidget import *
from lib.ClassFigure import *
from lib.BaseClass import *
from lib.Table import *
from CalcAverageFigure.CalcAverageFigure import *
import time
class ClassFigureCalcAverageFigure(ClassFigure):#改名
    def __init__(self,father):
        super().__init__(father)
    def draw_figure(self, **kwargs):
        super().draw_figure(**kwargs)
    def generate_FilenameSave(self):#每个类要重写
        return str(self.father.father.back.root.Main.generate_ImageLabel())+'_'+str(self.father.father.back.FigStart)+'-'+str(self.father.father.back.FigEnd)+'-AverageFigure.tif'
class ClassCalcAverageFigure(BaseFrame):#改名
    def __init__(self,father):
        self.father=father
        self.db=father.db
        self.back=self.father.back.CalcAverageFigure#改名
        super().__init__(self.father,padding=5,relief='sunken')
        self.FramePanel=ttk.Frame(self)
        self.FramePanel.grid(row=0,column=0)
        self.create_panel()
        self.Figure=ClassFigurePlus(self,ClassFigureCalcAverageFigure)#改名
        self.back.Figure=self.Figure
        self.Figure.grid(row=1,column=0)
        #以上为默认，不要动，以下可添加图片绑定功能self.Figure.Figure.bind('<Key>',self.CommandBindFigureKey)
    def create_panel(self):
        #R1
        self.FrameR1=ttk.Frame(self.FramePanel)
        self.FrameR1.pack(side='left')
        ttk.Button(self.FrameR1,text='彩色转黑白',command=self.CommandButtonProcess).pack(side='left')
        self.create_var('FigStart',self.back,'Int',0,True)
        self.create_var('FigEnd',self.back,'Int',0,True)
        self.LER1_1=LabelEntry(self.FrameR1,'起始帧：',self.FigStart)
        self.LER1_1.pack(side='left')
        self.LER1_1.entry.bind('<Return>',self.CommandBindFigStart)
        self.LER1_2=LabelEntry(self.FrameR1,'结束帧：',self.FigEnd)
        self.LER1_2.pack(side='left')
        self.LER1_2.entry.bind('<Return>',self.CommandBindFigEnd)
        ttk.Button(self.FramePanel,text='计算平均图',command=self.CommandButtonCalcAverage).pack(side='left')
        ttk.Button(self.FramePanel,text='Davis导出去前缀',command=self.CommandButtonRemovePrefix).pack(side='left')
    
    def CommandButtonProcess(self):
        start_time=time.time()
        print('彩色转黑白处理中，实验编号：'+str(self.db.Main.ExpNo))
        process_color_to_gray(self.db.Main.generate_fdir(),self.FigStart.get(),self.FigEnd.get(),self.db.Main.CoreNum)
        print('彩色转黑白处理完成，耗时',time.time()-start_time,'秒')

    def CommandBindFigStart(self,event):
        self.back.update('FigStart',self.FigStart.get(),False)
    def CommandBindFigEnd(self,event):
        self.back.update('FigEnd',self.FigEnd.get(),False)
    def CommandButtonCalcAverage(self):
        start_time=time.time()
        print('计算平均图中')
        self.FreshSelf(calculate_average_image(self.back.root.Main.generate_fdir(),self.FigStart.get(),self.FigEnd.get(),self.back.root.Main.CoreNum),False)
        print('计算完成，耗时',time.time()-start_time,'秒')
    
    def CommandButtonRemovePrefix(self):
        process_images(self.db.Main.generate_fdir())
        print('去除Davis导出前缀完成')
    def FreshSelf(self,img=np.random.randint(0,256,size=(640,704),dtype='uint8'),FlagFreshRange=True):
        self.Figure.Figure.change_figure(img)
        if FlagFreshRange:
            self.back.Fresh()
        self.Figure.CommandButtonR4_1()