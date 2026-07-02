import tkinter as tk
from tkinter import ttk
import cv2 as cv
from lib.lib_tkwidget import *
from lib.ClassFigure import *
from lib.BaseClass import *
from lib.Table import *
from lib.lib_Angle import *
from lib.excel_io import *
import time
import openpyxl
from MeasureFlameAngle.MeasureFlameAngle import *
from services.flame_angle_service import FlameAngleService

class ClassFigureMeasureFlameAngle(ClassFigure):
    def __init__(self,father):
        super().__init__(father)
        self.LINE_WIDTH=3
    def draw_line(self,originx,originy,angle,color=(255,255,255),length=1000):
        x2 = int(originx - length * np.cos(angle/180*np.pi))
        y2 = int(originy + length * np.sin(angle/180*np.pi))
        cv.line(self.img_show,(originx,originy),(x2,y2),color,self.LINE_WIDTH)
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
            cv.line(self.img_show,(0,HEIGHT//2),(WIDTH-1,HEIGHT//2),(255,255,255),self.LINE_WIDTH)
            cv.line(self.img_show,(WIDTH//2,0),(WIDTH//2,HEIGHT-1),(255,255,255),self.LINE_WIDTH)
        if self.back.FlagLineTheo:
            x1,y1=self.back.root.Main.FrameChoosePic.ImpactX,self.back.root.Main.FrameChoosePic.ImpactY
            # self.draw_line(x1,y1,-self.back.AngleO-90,(34,144,225))
            # self.draw_line(x1,y1,self.back.AngleF-90,(34,144,225))
            self.draw_line(x1,y1,-self.back.AngleCalc+90,(70,120,255))
        if self.back.FlagLineAngle:
            x1,y1=self.back.root.Main.FrameChoosePic.ImpactX,self.back.root.Main.FrameChoosePic.ImpactY
            # self.draw_line(x1,y1,self.back.AngleL,(255,153,153))
            # self.draw_line(x1,y1,self.back.AngleR,(255,153,153))
            self.draw_line(x1,y1,self.back.AngleM,(255,0,0))
        if self.back.FlagLineY:
            x1,y1=self.back.root.Main.FrameChoosePic.ImpactX,self.back.root.Main.FrameChoosePic.ImpactY
            self.img_show=cv.ellipse(self.img_show,(x1,y1),(self.back.YStart,self.back.YStart),0,180-self.back.AngleR,180-self.back.AngleL,(255,153,153),self.LINE_WIDTH)
            self.img_show=cv.ellipse(self.img_show,(x1,y1),(self.back.YEnd,self.back.YEnd),0,180-self.back.AngleR,180-self.back.AngleL,(255,153,153),self.LINE_WIDTH)
            # 以下是画Y线的
            # cv.line(self.img_show,(0,self.back.YStart),(WIDTH-1,self.back.YStart),(255,153,153),self.LINE_WIDTH)
            # cv.line(self.img_show,(0,self.back.YEnd),(WIDTH-1,self.back.YEnd),(255,153,153),self.LINE_WIDTH)
            # cv.line(self.img_show,(0,self.back.YCenter),(WIDTH-1,self.back.YCenter),(255,0,0),self.LINE_WIDTH)
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
        self.service=FlameAngleService()
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
        #R5
        ttk.Label(self.FramePanel,text='批量处理：').grid(row=4,column=0)
        self.create_var('FigStart',self.back,'Int',0,True)
        self.create_var('FigEnd',self.back,'Int',0,True)
        self.LER4_1=LabelEntry(self.FramePanel,'起始帧：',self.FigStart)
        self.LER4_1.grid(row=4,column=1,sticky='w')
        self.LER4_1.entry.bind('<Return>',self.CommandBindFigStart)
        self.LER4_2=LabelEntry(self.FramePanel,'结束帧：',self.FigEnd)
        self.LER4_2.grid(row=4,column=2,sticky='w')
        self.LER4_2.entry.bind('<Return>',self.CommandBindFigEnd)
        ttk.Button(self.FramePanel,text='批量处理火焰信息',command=self.CommandButtonCalcFlameAngle).grid(row=4,column=3,sticky='we')

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
    def CommandBindFigStart(self,event):
        self.back.update('FigStart',self.FigStart.get(),False)
    def CommandBindFigEnd(self,event):
        self.back.update('FigEnd',self.FigEnd.get(),False)

    def CommandButtonCalcFlameAngle(self):
        start_time=time.time()
        print('计算火焰信息中')
        settings={}
        for i in ['ScissorUp','ScissorDown','ScissorLeft','ScissorRight']:
            settings[i]=getattr(self.back,i)
        for i in ['Threshold']:
            settings[i]=getattr(self,i).get()
        for i in ['ImpactX','ImpactY']:
            settings[i]=getattr(self.father.back,i)
        res=self.service.calculate_lightweight_batch(self.back.root.Main.generate_fdir(),self.back.FigStart,self.back.FigEnd,self.back.root.Main.CoreNum,settings)
        calc_time=time.time()-start_time
        print('计算完成，耗时',calc_time,'秒')
        #写入文档
        wb=openpyxl.Workbook()
        ws=wb.active
        write_excel_mat(ws,list(zip(*settings.items())))#settings第一行是key，第二行是values，两行都是tuple格式
        write_excel_mat(ws,[['帧数','中心线角','左边界角','右边界角','火焰锥角','火焰起始','火焰结束','火焰长度']],True)
        write_excel_mat(ws,[['平均值']+list(np.mean(res,axis=0))[1:]],True)
        write_excel_mat(ws,[['标准差']+list(np.std(res,axis=0,ddof=1))[1:]],True)
        write_excel_mat(ws,res,True)
        fdir=r'E:\Sci\2023.3_mmhnto_combustion\第三次测量处理结果\火焰方向线提取火焰长度'
        if not os.path.exists(fdir):
            os.makedirs(fdir)
        wb.save(fdir+'/'+self.back.root.Main.generate_fdir().split('/')[-1]+'批处理结果.xlsx')

    def FreshSelf(self):
        # self.back.update_SheetData()
        img=cv.imdecode(np.fromfile(file=self.back.root.Main.FrameChoosePic.get_dir_tif(),dtype=np.uint8),-1)
        self.Figure.Figure.change_figure(img)
        self.back.Fresh()
        self.Figure.Figure.change_figure(img)
        self.back.update('FigStart',self.back.root.Main.FrameChoosePic.FigNameStart)
        self.back.update('FigEnd',self.back.root.Main.FrameChoosePic.FigNameEnd)
