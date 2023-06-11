import tkinter as tk
from tkinter import ttk
import cv2 as cv
from lib.lib_tkwidget import *
from lib.ClassFigure import *
from lib.BaseClass import *
from lib.Table import *
from lib.lib_Angle import *
from time import time
from CalcFlameAngle.CalcFlameAngle import *
from lib.excel_io import *
import openpyxl

class ClassCalcFlameAngle(BaseFrame):
    def __init__(self,father):
        self.father=father
        self.db=father.db
        self.back=self.father.back.CalcFlameAngle
        super().__init__(self.father,padding=5,relief='sunken')
        self.FramePanel=ttk.Frame(self)
        self.FramePanel.pack()
        self.create_panel()
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
        #R3
        self.create_var('ScissorUp',self.back,type='Int',init_value=0,FlagSave=True)
        self.create_var('ScissorDown',self.back,type='Int',init_value=0,FlagSave=True)
        self.create_var('ScissorLeft',self.back,type='Int',init_value=0,FlagSave=True)
        self.create_var('ScissorRight',self.back,type='Int',init_value=0,FlagSave=True)
        self.LE=[LabelEntry(self.FramePanel,text='上裁剪',var=self.ScissorUp),
                 LabelEntry(self.FramePanel,text='下裁剪',var=self.ScissorDown),
                 LabelEntry(self.FramePanel,text='左裁剪',var=self.ScissorLeft),
                 LabelEntry(self.FramePanel,text='右裁剪',var=self.ScissorRight)]
        for j,i in enumerate(self.LE):
            cache=['Up','Down','Left','Right']
            i.grid(row=2,column=j,sticky='w')
            i.entry.bind('<Return>',getattr(self,'CommandBindScissor'+cache[j]))
        #R4
        self.create_var('FigStart',self.back,'Int',0,True)
        self.create_var('FigEnd',self.back,'Int',0,True)
        self.LER4_1=LabelEntry(self.FramePanel,'起始帧：',self.FigStart)
        self.LER4_1.grid(row=3,column=0,sticky='w')
        self.LER4_1.entry.bind('<Return>',self.CommandBindFigStart)
        self.LER4_2=LabelEntry(self.FramePanel,'结束帧：',self.FigEnd)
        self.LER4_2.grid(row=3,column=1,sticky='w')
        self.LER4_2.entry.bind('<Return>',self.CommandBindFigEnd)
        self.create_var('FlagSave',self.back,type='Boolean',init_value=False)
        ttk.Checkbutton(self.FramePanel,onvalue=True,offvalue=False,
                        variable=self.FlagSave,command=self.CommandCheckButtonSave).grid(row=3,column=2,sticky='we')
        ttk.Button(self.FramePanel,text='开始计算',command=self.CommandButtonR4).grid(row=3,column=3,sticky='we')
    #R1
    def CommandBindGain(self,event):
        self.back.update('Gain',self.Gain.get(),False)
    def CommandBindThreshold(self,event):
        self.back.update('Threshold',self.Threshold.get(),False)
    #R2
    def CommandBindAngleO(self,event):
        self.back.update('AngleO',self.AngleO.get(),False)
    def CommandBindAngleF(self,event):
        self.back.update('AngleF',self.AngleF.get(),False)
    def CommandBindAngleCalc(self,event):
        self.back.update('AngleCalc',self.AngleCalc.get(),False)
    #R3
    def CommandBindScissorUp(self,event):
        self.back.update('ScissorUp',getattr(self,'ScissorUp').get())
        self.Figure.update_figure()
    def CommandBindScissorDown(self,event):
        self.back.update('ScissorDown',getattr(self,'ScissorDown').get())
        self.Figure.update_figure()
    def CommandBindScissorLeft(self,event):
        self.back.update('ScissorLeft',getattr(self,'ScissorLeft').get())
        self.Figure.update_figure()
    def CommandBindScissorRight(self,event):
        self.back.update('ScissorRight',getattr(self,'ScissorRight').get())
        self.Figure.update_figure()
    #R4
    def CommandBindFigStart(self,event):
        self.back.update('FigStart',self.FigStart.get(),False)
    def CommandBindFigEnd(self,event):
        self.back.update('FigEnd',self.FigEnd.get(),False)
    def CommandCheckButtonSave(self):
        self.back.update('FlagSave',self.FlagSave.get(),False)
    def CommandButtonR4(self):
        start_time=time()
        print('计算平均图中')
        settings={}
        for i in ['Gain','Threshold','AngleO','AngleF','AngleCalc','ScissorUp','ScissorDown','ScissorLeft','ScissorRight']:
            settings[i]=getattr(self,i).get()
        for i in ['ImpactX','ImpactY']:
            settings[i]=getattr(self.father.back,i)
        res=calc_flame_angle(self.back.root.Main.generate_fdir(),self.FigStart.get(),self.FigEnd.get(),self.back.root.Main.CoreNum,settings,self.FlagSave.get())
        #写入文档
        wb=openpyxl.Workbook()
        ws=wb.active
        write_excel_mat(ws,list(zip(*settings.items())))#settings第一行是key，第二行是values，两行都是tuple格式
        write_excel_mat(ws,[['帧数','中心线角','左边界角','右边界角','火焰锥角','火焰中心','火焰起始','火焰结束','火焰长度','火焰区平均强度','火焰区最大强度']],True)
        write_excel_mat(ws,[['平均值']+list(np.mean(res,axis=0))[1:]],True)
        write_excel_mat(ws,res,True)
        wb.save(self.back.root.Main.generate_fdir()+'/'+self.back.root.Main.generate_fdir().split('/')[-1]+'批处理结果.xlsx')
        print('计算完成，耗时',time()-start_time,'秒')
        
    def FreshSelf(self):
        pass