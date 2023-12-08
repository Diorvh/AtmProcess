import tkinter as tk
from tkinter import ttk
import cv2 as cv
from lib.lib_tkwidget import *
from lib.ClassFigure import *
from lib.BaseClass import *
from lib.Table import *
from PlayAtmAngle.PlayAtmAngle import *
import time
from lib.excel_io import *
import openpyxl
from lib.lib_tkPlot import *
from lib.dft import *
from CalcInductionLength.CalcInductionLength import *
class ClassFigureCalcInductionLength(ClassFigure):#改名
    def __init__(self,father):#back为本文件前端Class的back
        super().__init__(father)
    def draw_line(self,originx,originy,angle,color=(255,255,255),length=1000):
        x2 = int(originx - length * np.cos(angle/180*np.pi))
        y2 = int(originy + length * np.sin(angle/180*np.pi))
        cv.line(self.img_show,(originx,originy),(x2,y2),color,1)
    def draw_figure(self, **kwargs):
        self.img_show=self.img
        #默认处理方式，改成了基于现有img_show转8位处理
        if self.img.dtype=='uint16':
            self.img_show=np.array(np.floor(self.img_show/(2**8)),dtype='uint8')
        else:
            self.img_show=np.array(self.img_show,dtype='uint8')
        if len(self.img.shape)==2:
            self.img_show=cv.cvtColor(self.img_show,cv.COLOR_GRAY2RGB)
        #默认处理：裁剪和中心线显示
        self.img_show=self.Scissor(self.img_show,[self.back.ScissorUp,self.back.ScissorDown,self.back.ScissorLeft,self.back.ScissorRight])
        HEIGHT,WIDTH=self.img_show.shape[0],self.img_show.shape[1]
        if self.back.FlagCenterLine:
            cv.line(self.img_show,(0,HEIGHT//2),(WIDTH-1,HEIGHT//2),(255,255,255),1)
            cv.line(self.img_show,(WIDTH//2,0),(WIDTH//2,HEIGHT-1),(255,255,255),1)
        if self.back.FlagLineAngle:
            self.draw_line(self.back.root.Main.FrameChoosePic.ImpactX,self.back.root.Main.FrameChoosePic.ImpactY,self.back.AngleFlame,(255,0,0))
    def get_scissored_img(self):
        return self.Scissor(self.img,[self.back.ScissorUp,self.back.ScissorDown,self.back.ScissorLeft,self.back.ScissorRight])
    def generate_FilenameSave(self):#每个类要重写
        return str(self.back.root.Main.generate_ImageLabel())+'-InductionLength.tif'
class ClassCalcInductionLength(BaseFrame):#改名
    def __init__(self,father):
        self.father=father
        self.db=father.db
        self.back=self.father.back.CalcInductionLength#改名
        super().__init__(self.father,padding=5,relief='sunken')
        self.FramePanel=ttk.Frame(self)
        self.FramePanel.grid(row=0,column=0)
        self.create_panel()
        self.Figure=ClassFigurePlus(self,ClassFigureCalcInductionLength)#改名
        self.back.Figure=self.Figure
        self.Figure.grid(row=1,column=0,rowspan=2)
        #以上为默认，不要动，以下可添加图片绑定功能self.Figure.Figure.bind('<Key>',self.CommandBindFigureKey)
        self.PlotFrame1=PlotFrame(self,X_name='y/pix',Y_name='灰度值')#中心线上灰度值分布滤波后
        self.PlotFrame1.grid(row=2,column=1)
        self.PlotFrame2=PlotFrame(self,X_name='y/pix',Y_name='灰度值一阶差分')#灰度值差值的分布
        self.PlotFrame2.grid(row=1,column=1)
        self.PlotFrame3=PlotFrame(self,X_name='f/Hz',Y_name='幅值')#灰度值分布频域特性
        self.PlotFrame3.grid(row=1,column=2)
        self.PlotFrame4=PlotFrame(self,X_name='y/pix',Y_name='灰度值')#原始Gray
        self.PlotFrame4.grid(row=2,column=2)
    def create_panel(self):
        #R1
        self.FrameR1=ttk.Frame(self.FramePanel)
        self.FrameR1.pack()
        self.create_var('AngleFlame',self.back,'Double',0,True)
        self.LE1=LabelEntry(self.FrameR1,'火焰方向',self.AngleFlame)
        self.LE1.pack(side='left')
        self.LE1.entry.bind('<Return>',self.CommandBindAngleFlame)
        self.create_var('CutoffF',self.back,'Int',0,True)
        self.LE2=LabelEntry(self.FrameR1,'低通截止频率',self.CutoffF)
        self.LE2.pack(side='left')
        self.LE2.entry.bind('<Return>',self.CommandBindCutoffF)
        self.create_var('FlagLineAngle',self.back,'Boolean',False,True)
        self.Button=ttk.Button(self.FrameR1,text='显示锥角线',command=self.CommandButtonR1)
        self.Button.pack(side='left')
        #R2
        self.FrameR2=ttk.Frame(self.FramePanel)
        self.FrameR2.pack()
        self.create_var('InducL',self.back,'Double',0,True)
        self.create_var('AmpInducL',self.back,'Double',0,True)
        LabelLabel(self.FrameR2,'Induction Length',self.InducL).pack(side='left')#显示引导距离
        LabelLabel(self.FrameR2,'Induction Length Amplitude',self.AmpInducL).pack(side='left')#显示引导距离对应强度
    #R1
    def CommandButtonR1(self):
        self.back.update('FlagLineAngle',not self.FlagLineAngle.get())
        self.Button.config(text='关闭锥角线' if self.FlagLineAngle.get() else '显示锥角线')
        self.FreshSelf()
    def CommandBindAngleFlame(self,event):
        self.back.update('AngleFlame',self.AngleFlame.get(),False)
        self.FreshSelf()
    def CommandBindCutoffF(self,event):
        self.back.update('CutoffF',self.CutoffF.get(),False)
        self.FreshSelf()
    def FreshSelf(self):
        img=cv.imdecode(np.fromfile(file=self.back.root.Main.FrameChoosePic.get_dir_tif(),dtype=np.uint8),-1)
        self.Figure.Figure.change_figure(img)
        self.back.gray=calc_graydis_Angle(self.Figure.Figure.get_scissored_img(),self.back.root.Main.FrameChoosePic.ImpactX,self.back.root.Main.FrameChoosePic.ImpactY,self.back.AngleFlame)
        f,amp,phase=dft(self.back.gray,len(self.back.gray))
        graylowpass=lowpass(self.back.gray,len(self.back.gray),self.CutoffF.get())
        graydiff=calc_graydiff(graylowpass)
        self.PlotFrame1.update_data(list(range(len(graylowpass))),graylowpass)
        self.PlotFrame2.update_data(list(range(len(graydiff))),graydiff)
        self.PlotFrame3.update_data(list(range(len(amp)//2)),amp[:len(amp)//2])
        self.PlotFrame4.update_data(list(range(len(self.back.gray))),self.back.gray)
        self.InducL.set(np.argmax(graydiff[50:])+50)
        self.AmpInducL.set(np.max(graydiff[50:]))
        #写入文档
        wb=openpyxl.Workbook()
        ws=wb.active
        settings=[['火焰方向/°'],[self.back.AngleFlame]]
        write_excel_mat(ws,settings)
        write_excel_mat(ws,[['R/pix','灰度值']],True)
        write_excel_mat(ws,np.column_stack((np.array(range(len(self.back.gray))),self.back.gray)),True)
        fdir=r'E:\Sci\2023.3_mmhnto_combustion\第三次测量处理结果\火焰方向线上强度分布'
        if not os.path.exists(fdir):
            os.makedirs(fdir)
        wb.save(fdir+'/'+self.back.root.Main.DirDirect.split('/')[-1]+'火焰方向线上强度分布结果.xlsx')

