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
#R1图像预处理，2个绘图Flag
#R2锥角起点
#R3计算区域，1个绘图Flag
#R4滤波参数
#R5锥角提取区域，1个绘图Flag
#R6锥角提取结果，1个绘图Flag
#R7批量处理
class ClassFigurePlayAtmAngle(ClassFigure):#改名
    def __init__(self,father):#back为本文件前端Class的back
        super().__init__(father)
    def draw_line(self,originx,originy,angle,color=(255,255,255),length=1000):
        x2 = int(originx - length * np.cos(angle/180*np.pi))
        y2 = int(originy + length * np.sin(angle/180*np.pi))
        cv.line(self.img_show,(originx,originy),(x2,y2),color,1)
    def draw_figure(self, **kwargs):
        self.img_show=self.img
        #R1图像预处理
        if self.back.FlagReverseColor:
            self.img_show=65535-self.img_show
        if self.back.FlagBinary:
            ret, self.img_show = cv.threshold(self.img_show, self.back.ThresBinary, 65535, cv.THRESH_BINARY)
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
        #R3计算区域显示
        if self.back.FlagCalcArea:
            self.img_show=cv.ellipse(self.img_show,(self.back.XLeft,self.back.Y),(self.back.Rmax,self.back.Rmax),0,90,180-self.back.ThetaLeft*0.1,(0,0,255),1)
            self.img_show=cv.ellipse(self.img_show,(self.back.XRight,self.back.Y),(self.back.Rmax,self.back.Rmax),0,180-self.back.ThetaRight*0.1,90,(0,0,255),1)
        #R5计算区域显示
        if self.back.FlagExtractRange:
            self.draw_line(self.back.XLeft,self.back.Y,self.back.ThetaRangeLeft1*0.1,(255,0,0))
            self.draw_line(self.back.XLeft,self.back.Y,self.back.ThetaRangeLeft2*0.1,(255,0,0))
            self.draw_line(self.back.XRight,self.back.Y,self.back.ThetaRangeRight1*0.1,(255,0,0))
            self.draw_line(self.back.XRight,self.back.Y,self.back.ThetaRangeRight2*0.1,(255,0,0))
        #R6雾化锥角线显示
        if self.back.FlagLineAngle:
            self.draw_line(self.back.XLeft,self.back.Y,self.back.AngleL,(0,255,0))
            self.draw_line(self.back.XRight,self.back.Y,self.back.AngleR,(0,255,0))
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
        self.AF=PlotFrame(self,[1],[1])
        self.AF.grid(row=1,column=1)
        self.BF=PlotFrame(self,[1],[1])
        self.BF.grid(row=2,column=1)
        self.AFF=PlotFrame(self,[1],[1])#滤波
        self.AFF.grid(row=1,column=2)
        self.BFF=PlotFrame(self,[1],[1])#滤波
        self.BFF.grid(row=2,column=2)
        self.AFFF=PlotFrame(self,[1],[1])#滤波后一阶导
        self.AFFF.grid(row=1,column=3)
        self.BFFF=PlotFrame(self,[1],[1])#滤波后一阶导
        self.BFFF.grid(row=2,column=3)
        self.AFFFF=PlotFrame(self,[1],[1])#滤波后二阶导
        self.AFFFF.grid(row=1,column=4)
        self.BFFFF=PlotFrame(self,[1],[1])#滤波后二阶导
        self.BFFFF.grid(row=2,column=4)
        self.Figure=ClassFigurePlus(self,ClassFigurePlayAtmAngle)#改名
        self.back.Figure=self.Figure
        self.Figure.grid(row=1,column=0,rowspan=2)
        #以上为默认，不要动，以下可添加图片绑定功能self.Figure.Figure.bind('<Key>',self.CommandBindFigureKey)
    def create_panel(self):
        #R1
        ttk.Label(self.FramePanel,text='图像预处理：').grid(row=0,column=0)
        self.create_var('FlagReverseColor',self.back,'Boolean',False,True)
        self.create_var('FlagBinary',self.back,'Boolean',False,True)
        self.create_var('ThresBinary',self.back,'Int',0,True)
        self.ButtonR1_1=ttk.Button(self.FramePanel,text='颜色翻转',command=self.CommandButtonReverseColor)
        self.ButtonR1_1.grid(row=0,column=1,sticky='w')
        self.ButtonR1_2=ttk.Button(self.FramePanel,text='二值化处理',command=self.CommandButtonBinary)
        self.ButtonR1_2.grid(row=0,column=2,sticky='w')
        self.LER1_1=LabelEntry(self.FramePanel,'二值化阈值=',self.ThresBinary)
        self.LER1_1.grid(row=0,column=3,sticky='w')
        self.LER1_1.entry.bind('<Return>',self.CommandBindThresBinary)
        #R2
        ttk.Label(self.FramePanel,text='锥角起点：').grid(row=1,column=0)
        self.create_var('XLeft',self.back,'Int',0,True)
        self.create_var('XRight',self.back,'Int',0,True)
        self.create_var('Y',self.back,'Int',0,True)
        self.LER2_1=LabelEntry(self.FramePanel,'左点X=',self.XLeft)
        self.LER2_1.grid(row=1,column=1,sticky='w')
        self.LER2_1.entry.bind('<Return>',self.CommandBindXLeft)
        self.LER2_2=LabelEntry(self.FramePanel,'右点X=',self.XRight)
        self.LER2_2.grid(row=1,column=2,sticky='w')
        self.LER2_2.entry.bind('<Return>',self.CommandBindXRight)
        self.LER2_3=LabelEntry(self.FramePanel,'Y=',self.Y)
        self.LER2_3.grid(row=1,column=3,sticky='w')
        self.LER2_3.entry.bind('<Return>',self.CommandBindY)
        #R3
        ttk.Label(self.FramePanel,text='计算区域：').grid(row=2,column=0)
        self.create_var('Rmax',self.back,'Int',1000,True)
        self.create_var('ThetaLeft',self.back,'Int',-1,True)
        self.create_var('ThetaRight',self.back,'Int',1801,True)
        self.LER3_1=LabelEntry(self.FramePanel,'Rmax=',self.Rmax)
        self.LER3_1.grid(row=2,column=1,sticky='w')
        self.LER3_1.entry.bind('<Return>',self.CommandBindRmax)
        self.LER3_2=LabelEntry(self.FramePanel,'ThetaLeft=',self.ThetaLeft,extratext='*0.1°')
        self.LER3_2.grid(row=2,column=2,sticky='w')
        self.LER3_2.entry.bind('<Return>',self.CommandBindThetaLeft)
        self.LER3_3=LabelEntry(self.FramePanel,'ThetaRight=',self.ThetaRight,extratext='*0.1°')
        self.LER3_3.grid(row=2,column=3,sticky='w')
        self.LER3_3.entry.bind('<Return>',self.CommandBindThetaRight)
        self.create_var('FlagCalcArea',self.back,'Boolean',False,True)
        self.ButtonR3=ttk.Button(self.FramePanel,text='显示计算区域',command=self.CommandButtonR3)
        self.ButtonR3.grid(row=2,column=4,sticky='we')
        #R4
        ttk.Label(self.FramePanel,text='滤波参数：').grid(row=3,column=0)
        self.create_var('window_length',self.back,'Int',100,True)
        self.create_var('polyorder',self.back,'Int',2,True)
        self.LER4_1=LabelEntry(self.FramePanel,'window_length=',self.window_length)
        self.LER4_1.grid(row=3,column=1,sticky='w')
        self.LER4_1.entry.bind('<Return>',self.CommandBindwindow_length)
        self.LER4_2=LabelEntry(self.FramePanel,'polyorder=',self.polyorder)
        self.LER4_2.grid(row=3,column=2,sticky='w')
        self.LER4_2.entry.bind('<Return>',self.CommandBindpolyorder)
        #R5
        ttk.Label(self.FramePanel,text='锥角提取范围：').grid(row=4,column=0)
        self.create_var('ThetaRangeLeft1',self.back,'Int',-1,True)
        self.create_var('ThetaRangeLeft2',self.back,'Int',900,True)
        self.create_var('ThetaRangeRight1',self.back,'Int',900,True)
        self.create_var('ThetaRangeRight2',self.back,'Int',1801,True)
        #R5-1
        self.FrameR5_1=ttk.Frame(self.FramePanel)
        self.FrameR5_1.grid(row=4,column=1,columnspan=2)
        ttk.Label(self.FrameR5_1,text='左侧').pack(side='left')
        self.EntryR5_1=ttk.Entry(self.FrameR5_1,textvariable=self.ThetaRangeLeft1)
        self.EntryR5_1.pack(side='left')
        self.EntryR5_1.bind('<Return>',self.CommandThetaRangeLeft1)
        ttk.Label(self.FrameR5_1,text='*0.1°-').pack(side='left')
        self.EntryR5_2=ttk.Entry(self.FrameR5_1,textvariable=self.ThetaRangeLeft2)
        self.EntryR5_2.pack(side='left')
        self.EntryR5_2.bind('<Return>',self.CommandThetaRangeLeft2)
        ttk.Label(self.FrameR5_1,text='*0.1°').pack(side='left')
        #R5-2
        self.FrameR5_2=ttk.Frame(self.FramePanel)
        self.FrameR5_2.grid(row=4,column=3,columnspan=2)
        ttk.Label(self.FrameR5_2,text='右侧').pack(side='left')
        self.EntryR5_3=ttk.Entry(self.FrameR5_2,textvariable=self.ThetaRangeRight1)
        self.EntryR5_3.pack(side='left')
        self.EntryR5_3.bind('<Return>',self.CommandThetaRangeRight1)
        ttk.Label(self.FrameR5_2,text='*0.1°-').pack(side='left')
        self.EntryR5_4=ttk.Entry(self.FrameR5_2,textvariable=self.ThetaRangeRight2)
        self.EntryR5_4.pack(side='left')
        self.EntryR5_4.bind('<Return>',self.CommandThetaRangeRight2)
        ttk.Label(self.FrameR5_2,text='*0.1°').pack(side='left')
        self.create_var('FlagExtractRange',self.back,'Boolean',False,True)
        self.ButtonR5=ttk.Button(self.FramePanel,text='显示提取区域',command=self.CommandButtonR5)
        self.ButtonR5.grid(row=4,column=5,sticky='we')
        #R6
        self.create_var('AngleL',self.back,'Double',0,True)
        self.create_var('AngleR',self.back,'Double',0,True)
        self.create_var('Angle',self.back,'Double',0,True)
        LabelLabel(self.FramePanel,'左边界角=',self.AngleL,extratext='°').grid(row=5,column=0,sticky='w')
        LabelLabel(self.FramePanel,'右边界角=',self.AngleR,extratext='°').grid(row=5,column=1,sticky='w')
        LabelLabel(self.FramePanel,'雾化锥角=',self.Angle,extratext='°').grid(row=5,column=2,sticky='w')
        self.create_var('FlagLineAngle',self.back,'Boolean',False,True)
        self.ButtonR6=ttk.Button(self.FramePanel,text='显示锥角线',command=self.CommandButtonR6)
        self.ButtonR6.grid(row=5,column=3,sticky='we')
        #R7
        self.create_var('FigStart',self.back,'Int',0,True)
        self.create_var('FigEnd',self.back,'Int',0,True)
        self.LER7_1=LabelEntry(self.FramePanel,'起始帧：',self.FigStart)
        self.LER7_1.grid(row=7,column=0,sticky='w')
        self.LER7_1.entry.bind('<Return>',self.CommandBindFigStart)
        self.LER7_2=LabelEntry(self.FramePanel,'结束帧：',self.FigEnd)
        self.LER7_2.grid(row=7,column=1,sticky='w')
        self.LER7_2.entry.bind('<Return>',self.CommandBindFigEnd)
        ttk.Button(self.FramePanel,text='批量处理雾化锥角',command=self.CommandButtonCalcAtmAngle).grid(row=7,column=2,sticky='w')
    #R1
    def CommandButtonReverseColor(self):
        self.back.update('FlagReverseColor',not self.FlagReverseColor.get())
        self.ButtonR1_1.config(text='颜色还原' if self.FlagReverseColor.get() else '颜色翻转')
        self.FreshSelf()
    def CommandButtonBinary(self):
        self.back.update('FlagBinary',not self.FlagBinary.get())
        self.ButtonR1_2.config(text='二值化还原' if self.FlagBinary.get() else '二值化处理')
        self.FreshSelf()
    def CommandBindThresBinary(self,event):
        self.back.update('ThresBinary',self.ThresBinary.get(),False)
        self.FreshSelf()
    #R2
    def CommandBindXLeft(self,event):
        self.back.update('XLeft',self.XLeft.get(),False)
        self.FreshSelf()
    def CommandBindXRight(self,event):
        self.back.update('XRight',self.XRight.get(),False)
        self.FreshSelf()
    def CommandBindY(self,event):
        self.back.update('Y',self.Y.get(),False)
        self.FreshSelf()
    #R3
    def CommandBindRmax(self,event):
        self.back.update('Rmax',self.Rmax.get(),False)
        self.FreshSelf()
    def CommandBindThetaLeft(self,event):
        self.back.update('ThetaLeft',self.ThetaLeft.get(),False)
        self.FreshSelf()
    def CommandBindThetaRight(self,event):
        self.back.update('ThetaRight',self.ThetaRight.get(),False)
        self.FreshSelf()
    def CommandButtonR3(self):
        self.back.update('FlagCalcArea',not self.FlagCalcArea.get())
        self.ButtonR3.config(text='关闭计算区域显示' if self.FlagCalcArea.get() else '显示计算区域')
        self.FreshSelf()
    #R4
    def CommandBindwindow_length(self,event):
        self.back.update('window_length',self.window_length.get(),False)
        self.FreshSelf()
    def CommandBindpolyorder(self,event):
        self.back.update('polyorder',self.polyorder.get(),False)
        self.FreshSelf()
    #R5
    def CommandThetaRangeLeft1(self,event):
        self.back.update('ThetaRangeLeft1',self.ThetaRangeLeft1.get(),False)
        self.FreshSelf()
    def CommandThetaRangeLeft2(self,event):
        self.back.update('ThetaRangeLeft2',self.ThetaRangeLeft2.get(),False)
        self.FreshSelf()
    def CommandThetaRangeRight1(self,event):
        self.back.update('ThetaRangeRight1',self.ThetaRangeRight1.get(),False)
        self.FreshSelf()
    def CommandThetaRangeRight2(self,event):
        self.back.update('ThetaRangeRight2',self.ThetaRangeRight2.get(),False)
        self.FreshSelf()    
    def CommandButtonR5(self):
        self.back.update('FlagExtractRange',not self.FlagExtractRange.get())
        self.ButtonR5.config(text='关闭提取区域' if self.FlagExtractRange.get() else '显示提取区域')
        self.FreshSelf()
    #R6
    def CommandButtonR6(self):
        self.back.update('FlagLineAngle',not self.FlagLineAngle.get())
        self.ButtonR6.config(text='关闭锥角线' if self.FlagLineAngle.get() else '显示锥角线')
        self.FreshSelf()
    #R7
    def CommandBindFigStart(self,event):
        self.back.update('FigStart',self.FigStart.get(),False)
    def CommandBindFigEnd(self,event):
        self.back.update('FigEnd',self.FigEnd.get(),False)
    def CommandButtonCalcAtmAngle(self):
        start_time=time.time()
        # calculate_atmangle(self.back.root.Main.generate_fdir(),self.FigStart.get(),self.FigEnd.get(),self.back.root.Main.CoreNum))
        print('计算雾化锥角中，实验编号：'+str(self.db.Main.ExpNo))
        settings={}
        for i in ['XLeft','XRight']:
            settings[i]=getattr(self,i).get()
        settings['XMid']=self.father.back.ImpactX
        for i in ['Y','Thres']:
            settings[i]=getattr(self,i).get()
        res=[]#mul_calculate_atmangle(self.back.root.Main.generate_fdir(),self.FigStart.get(),self.FigEnd.get(),self.back.root.Main.CoreNum,settings)
        #写入文档
        wb=openpyxl.Workbook()
        ws=wb.active
        write_excel_mat(ws,list(zip(*settings.items())))#settings第一行是key，第二行是values，两行都是tuple格式
        write_excel_mat(ws,[['帧数','中心线角','左边界角','右边界角','雾化锥角']],True)
        write_excel_mat(ws,[['平均值']+list(np.mean(res,axis=0))[1:]],True)
        write_excel_mat(ws,[['标准差']+list(np.std(res,axis=0))[1:]],True)
        write_excel_mat(ws,[['相对标准差%']+list(np.std(res,axis=0)/np.mean(res,axis=0)*100)[1:]],True)
        write_excel_mat(ws,res,True)
        wb.save(self.back.root.Main.generate_fdir()+'/'+self.back.root.Main.generate_fdir().split('/')[-1]+'批处理结果.xlsx')
        print('计算完成，耗时',time.time()-start_time,'秒')

    def FreshSelf(self):
        img=cv.imdecode(np.fromfile(file=self.back.root.Main.FrameChoosePic.get_dir_tif(),dtype=np.uint8),-1)
        self.Figure.Figure.change_figure(img)
        self.back.Fresh()
        self.Figure.Figure.change_figure(img)
        self.AF.update_data(self.back.resL[0],self.back.resL[1])
        self.BF.update_data(self.back.resR[0],self.back.resR[1])
        self.AFF.update_data(self.back.resLSG[0],self.back.resLSG[1])
        self.BFF.update_data(self.back.resRSG[0],self.back.resRSG[1])
        self.AFFF.update_data(self.back.resLSGdiff1[0],self.back.resLSGdiff1[1])
        self.BFFF.update_data(self.back.resRSGdiff1[0],self.back.resRSGdiff1[1])
        self.AFFFF.update_data(self.back.resLSGdiff2[0],self.back.resLSGdiff2[1])
        self.BFFFF.update_data(self.back.resRSGdiff2[0],self.back.resRSGdiff2[1])