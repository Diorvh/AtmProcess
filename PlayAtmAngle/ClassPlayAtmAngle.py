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
        self.FrameR1.pack()
        self.create_var('FlagReverseColor',self.back,'Boolean',False,True)
        self.ButtonR1_1=ttk.Button(self.FrameR1,text='颜色翻转',command=self.CommandButtonReverseColor)
        self.ButtonR1_1.pack(side='left')
        self.create_var('FlagBinary',self.back,'Boolean',False,True)
        self.ButtonR1_2=ttk.Button(self.FrameR1,text='二值化处理',command=self.CommandButtonBinary)
        self.ButtonR1_2.pack(side='left')
        self.create_var('ThresBinary',self.back,'Int',0,True)
        self.LER1_1=LabelEntry(self.FrameR1,'二值化阈值=',self.ThresBinary)
        self.LER1_1.pack(side='left')
        self.LER1_1.entry.bind('<Return>',self.CommandBindThresBinary)
        #R2
        self.FrameR2=ttk.Frame(self.FramePanel)
        self.FrameR2.pack()
        self.create_var('FlagMinusBG',self.back,'Boolean',False,True)
        ttk.Checkbutton(self.FrameR2,onvalue=True,offvalue=False,
                        variable=self.FlagMinusBG,command=self.CommandCheckButtonFlagMinusBG).pack(side='left')
        ttk.Label(self.FrameR2,text='减背景').pack(side='left')
        self.create_var('DirBG',self.back,'String','',True)
        ChooseFile(self.FrameR2,'背景图片目录：',self.DirBG).pack(side='left')
        self.create_var('BGYStart',self.back,'Int',0,True)
        self.LER2_1=LabelEntry(self.FrameR2,'背景起始y坐标=',self.BGYStart)
        self.LER2_1.pack(side='left')
        self.LER2_1.entry.bind('<Return>',self.CommandBindBGYStart)
        #R3
        self.FrameR3=ttk.Frame(self.FramePanel)
        self.FrameR3.pack()
        self.create_var('FlagMinusLast',self.back,'Boolean',False,True)
        ttk.Checkbutton(self.FrameR3,onvalue=True,offvalue=False,
                        variable=self.FlagMinusLast,command=self.CommandCheckButtonFlagMinusLast).pack(side='left')
        ttk.Label(self.FrameR3,text='减上一张').pack(side='left')

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
        self.ButtonR1_1.config(text='颜色还原' if self.FlagReverseColor.get() else '颜色翻转')
        self.FreshSelf()
    def CommandButtonBinary(self):
        self.back.update('FlagBinary',not self.FlagBinary.get())
        self.ButtonR1_1.config(text='二值化还原' if self.FlagBinary.get() else '二值化处理')
        self.FreshSelf()
    def CommandBindThresBinary(self):
        self.back.update('ThresBinary',self.ThresBinary.get(),False)
    def CommandCheckButtonFlagMinusBG(self):
        self.back.update('FlagMinusBG',self.FlagMinusBG.get(),False)
    def CommandBindBGYStart(self):
        self.back.update('BGYStart',self.BGYStart.get(),False)
    def CommandCheckButtonFlagMinusLast(self):
        self.back.update('FlagMinusLast',self.FlagMinusLast.get(),False)



    # def CommandButtonCalcAverage(self):
    #     start_time=time.time()
    #     print('计算平均图中')
    #     self.FreshSelf(calculate_average_image(self.back.root.Main.generate_fdir(),self.FigStart.get(),self.FigEnd.get(),self.back.root.Main.CoreNum))
    #     print('计算完成，耗时',time.time()-start_time,'秒')

    def FreshSelf(self):
        img=cv.imdecode(np.fromfile(file=self.back.root.Main.FrameChoosePic.get_dir_tif(),dtype=np.uint8),-1)
        self.Figure.Figure.change_figure(img)
        self.back.Fresh()