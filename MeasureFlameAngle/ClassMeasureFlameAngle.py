import tkinter as tk
from tkinter import ttk
import cv2 as cv
from lib.lib_tkwidget import *
from lib.ClassFigure import *
from lib.BaseClass import *
from lib.Table import *
from lib.lib_Angle import *

class ClassFigureMeasureFlameAngle(ClassFigure):
    def __init__(self,father):
        super().__init__(father)
    def draw_line(self,originx,originy,angle,color=(255,255,255),length=1000):
        x2 = int(originx - length * np.cos(angle/180*np.pi))
        y2 = int(originy + length * np.sin(angle/180*np.pi))
        cv.line(self.img_show,(originx,originy),(x2,y2),color,1)
    def draw_figure(self, **kwargs):
        #重新复制
        if self.img.dtype=='uint16':
            self.img_show=np.array(np.round(self.img/(2**8)),dtype='uint8')
        else:
            self.img_show=np.array(self.img,dtype='uint8')
        self.img_show=(self.img_show*self.back.Gain).astype('uint8')#增益
        if self.back.FlagPColor:#伪彩图
            self.img_show=cv.applyColorMap(self.img_show,cv.COLORMAP_JET)
            self.img_show=cv.cvtColor(self.img_show,cv.COLOR_BGR2RGB)
        elif len(self.img.shape)==2:
            self.img_show=cv.cvtColor(self.img_show,cv.COLOR_GRAY2RGB)
        #默认处理：裁剪和中心线显示
        self.img_show=self.Scissor(self.img_show,[self.back.ScissorUp,self.back.ScissorDown,self.back.ScissorLeft,self.back.ScissorRight])
        HEIGHT,WIDTH=self.img_show.shape[0],self.img_show.shape[1]
        if self.back.FlagCenterLine:
            cv.line(self.img_show,(0,HEIGHT//2),(WIDTH-1,HEIGHT//2),(255,255,255),1)
            cv.line(self.img_show,(WIDTH//2,0),(WIDTH//2,HEIGHT-1),(255,255,255),1)
        if self.back.FlagLineTheo:
            x1,y1=self.back.root.Main.FrameChoosePic.ImpactX,self.back.root.Main.FrameChoosePic.ImpactY
            self.draw_line(x1,y1,-self.back.AngleO-90,(255,255,255))
            self.draw_line(x1,y1,self.back.AngleF-90,(255,255,255))
            self.draw_line(x1,y1,-self.back.AngleCalc+90,(255,255,255))
        if self.back.FlagLineAngle:
            x1,y1=self.back.root.Main.FrameChoosePic.ImpactX,self.back.root.Main.FrameChoosePic.ImpactY
            self.draw_line(x1,y1,self.back.AngleL,(255,0,0))
            self.draw_line(x1,y1,self.back.AngleR,(255,0,0))
            self.draw_line(x1,y1,self.back.AngleM,(0,255,0))
        if self.back.FlagLineY:
            cv.line(self.img_show,(0,self.back.YStart),(WIDTH-1,self.back.YStart),(255,0,0),1)
            cv.line(self.img_show,(0,self.back.YEnd),(WIDTH-1,self.back.YEnd),(255,0,0),1)
            cv.line(self.img_show,(0,self.back.YCenter),(WIDTH-1,self.back.YCenter),(0,255,0),1)
    def generate_FilenameSave(self):#每个类要重写
        if self.back.root.Main.FlagDirect:
            name=self.back.root.Main.DirDirect.split('/')[-1][:-4]
            if self.back.FlagPColor:
                name+='-伪彩图'
            if self.back.FlagLineTheo:
                name+='-理论线'
            if self.back.FlagLineAngle:
                name+='-锥角线'
            if self.back.FlagLineY:
                name+='-长度线'
            return name+'.tif'
        return self.back.root.Main.Other+'_'+str(self.back.root.Main.FrameChoosePic.FigName)+'.tif'
class ClassMeasureFlameAngle(BaseFrame):
    def __init__(self,father):
        self.father=father
        self.db=father.db
        self.back=self.father.back.MeasureFlameAngle
        super().__init__(self.father,padding=5,relief='sunken')
        self.FramePanel=ttk.Frame(self)
        self.FramePanel.grid(row=0,column=0)
        self.create_panel()
        self.Figure=ClassFigurePlus(self,ClassFigureMeasureFlameAngle)
        self.back.Figure=self.Figure
        self.Figure.grid(row=1,column=0)
    def create_panel(self):
        #R1
        self.create_var('Gain',self.back,'Double',1,True)
        self.create_var('Threshold',self.back,'Double',0.1,True)
        self.LER1_1=LabelEntry(self.FramePanel,'增益=',self.Gain)
        self.LER1_1.grid(row=0,column=0,columnspan=2,sticky='w')
        self.LER1_1.entry.bind('<Return>',self.CommandBindGain)
        self.LER1_2=LabelEntry(self.FramePanel,'单侧阈值=',self.Threshold)
        self.LER1_2.grid(row=0,column=2,columnspan=2,sticky='w')
        self.LER1_2.entry.bind('<Return>',self.CommandBindThreshold)
        self.create_var('FlagPColor',self.back,'Boolean',False,True)
        self.ButtonR1=ttk.Button(self.FramePanel,text='显示伪彩图',command=self.CommandButtonR1)
        self.ButtonR1.grid(row=0,column=4,sticky='we')
        #R2
        self.create_var('AngleO',self.back,'Double',0,True)
        self.create_var('AngleF',self.back,'Double',0,True)
        self.create_var('AngleCalc',self.back,'Double',0,True)
        self.LER2_1=LabelEntry(self.FramePanel,'氧化剂夹角=',self.AngleO)
        self.LER2_1.grid(row=1,column=0,sticky='w')
        self.LER2_1.entry.bind('<Return>',self.CommandBindAngleO)
        self.LER2_2=LabelEntry(self.FramePanel,'燃料夹角=',self.AngleF)
        self.LER2_2.grid(row=1,column=1,sticky='w')
        self.LER2_2.entry.bind('<Return>',self.CommandBindAngleF)
        self.LER2_3=LabelEntry(self.FramePanel,'合成动量夹角(O+)=',self.AngleCalc)
        self.LER2_3.grid(row=1,column=2,columnspan=2,sticky='w')
        self.LER2_3.entry.bind('<Return>',self.CommandBindAngleCalc)
        self.create_var('FlagLineTheo',self.back,'Boolean',False,True)
        self.ButtonR2=ttk.Button(self.FramePanel,text='显示理论线',command=self.CommandButtonR2)
        self.ButtonR2.grid(row=1,column=4,sticky='we')
        #R3
        self.create_var('AngleL',self.back,'Double',0,True)
        self.create_var('AngleR',self.back,'Double',0,True)
        self.create_var('AngleM',self.back,'Double',0,True)
        self.create_var('Angle',self.back,'Double',0,True)
        LabelLabel(self.FramePanel,'左边界角=',self.AngleL,extratext='°').grid(row=2,column=0,sticky='w')
        LabelLabel(self.FramePanel,'右边界角=',self.AngleR,extratext='°').grid(row=2,column=1,sticky='w')
        LabelLabel(self.FramePanel,'中心线角=',self.AngleM,extratext='°').grid(row=2,column=2,sticky='w')
        LabelLabel(self.FramePanel,'火焰锥角=',self.Angle,extratext='°').grid(row=2,column=3,sticky='w')
        self.create_var('FlagLineAngle',self.back,'Boolean',False,True)
        self.ButtonR3=ttk.Button(self.FramePanel,text='显示锥角线',command=self.CommandButtonR3)
        self.ButtonR3.grid(row=2,column=4,sticky='we')
        #R4
        self.create_var('YStart',self.back,'Double',0,True)
        self.create_var('YEnd',self.back,'Double',0,True)
        self.create_var('YCenter',self.back,'Double',0,True)
        self.create_var('YLength',self.back,'Double',0,True)
        LabelLabel(self.FramePanel,'火焰起始=',self.YStart,extratext='pix').grid(row=3,column=0,sticky='w')
        LabelLabel(self.FramePanel,'火焰结束=',self.YEnd,extratext='pix').grid(row=3,column=1,sticky='w')
        LabelLabel(self.FramePanel,'火焰中心=',self.YCenter,extratext='pix').grid(row=3,column=2,sticky='w')
        LabelLabel(self.FramePanel,'火焰长度=',self.YLength,extratext='pix').grid(row=3,column=3,sticky='w')
        self.create_var('FlagLineY',self.back,'Boolean',False,True)
        self.ButtonR4=ttk.Button(self.FramePanel,text='显示火焰长度线',command=self.CommandButtonR4)
        self.ButtonR4.grid(row=3,column=4,sticky='we')

    def CommandBindGain(self,event):
        self.back.update('Gain',self.Gain.get(),False)
        self.FreshSelf()
    def CommandBindThreshold(self,event):
        self.back.update('Threshold',self.Threshold.get(),False)
        self.FreshSelf()
    def CommandButtonR1(self):
        self.back.update('FlagPColor',not self.FlagPColor.get())
        self.ButtonR1.config(text='关闭伪彩图' if self.FlagPColor.get() else '显示伪彩图')
        self.FreshSelf()

    def CommandBindAngleO(self,event):
        self.back.update('AngleO',self.AngleO.get(),False)
        self.FreshSelf()
    def CommandBindAngleF(self,event):
        self.back.update('AngleF',self.AngleF.get(),False)
        self.FreshSelf()
    def CommandBindAngleCalc(self,event):
        self.back.update('AngleCalc',self.AngleCalc.get(),False)
        self.FreshSelf()
    def CommandButtonR2(self):
        self.back.update('FlagLineTheo',not self.FlagLineTheo.get())
        self.ButtonR2.config(text='关闭理论线' if self.FlagLineTheo.get() else '显示理论线')
        self.FreshSelf()

    def CommandButtonR3(self):
        self.back.update('FlagLineAngle',not self.FlagLineAngle.get())
        self.ButtonR3.config(text='关闭锥角线' if self.FlagLineAngle.get() else '显示锥角线')
        self.FreshSelf()

    def CommandButtonR4(self):
        self.back.update('FlagLineY',not self.FlagLineY.get())
        self.ButtonR4.config(text='关闭火焰长度线' if self.FlagLineY.get() else '显示火焰长度线')
        self.FreshSelf()    

    def FreshSelf(self):
        # self.back.update_SheetData()
        img=cv.imdecode(np.fromfile(file=self.back.root.Main.FrameChoosePic.get_dir_tif(),dtype=np.uint8),-1)
        self.Figure.Figure.change_figure(img)
        self.back.Fresh()
        self.Figure.Figure.change_figure(img)