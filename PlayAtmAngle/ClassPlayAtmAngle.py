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
class ClassFigurePlayAtmAngle(ClassFigure):#改名
    def __init__(self,father):#back为本文件前端Class的back
        super().__init__(father)
    def draw_line(self,originx,originy,angle,color=(255,255,255),length=1000):
        x2 = int(originx - length * np.cos(angle/180*np.pi))
        y2 = int(originy + length * np.sin(angle/180*np.pi))
        cv.line(self.img_show,(originx,originy),(x2,y2),color,1)
    def draw_figure(self, **kwargs):
        self.img_show=self.img
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
        if self.back.FlagLineAngle:
            self.draw_line(self.back.XLeft,self.back.Y,self.back.AngleL,(255,0,0))
            self.draw_line(self.back.root.Main.FrameChoosePic.ImpactX,self.back.Y,self.back.AngleM,(0,255,0))
            self.draw_line(self.back.XRight,self.back.Y,self.back.AngleR,(255,0,0))
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
        self.AAF=PlotFrame(self,[1],[1])#梯度
        self.AAF.grid(row=1,column=2)
        self.BBF=PlotFrame(self,[1],[1])#梯度
        self.BBF.grid(row=2,column=2)
        self.AAAF=PlotFrame(self,[1],[1])#梯度2
        self.AAAF.grid(row=1,column=3)
        self.BBBF=PlotFrame(self,[1],[1])#梯度2
        self.BBBF.grid(row=2,column=3)
        self.Figure=ClassFigurePlus(self,ClassFigurePlayAtmAngle)#改名
        self.back.Figure=self.Figure
        self.Figure.grid(row=1,column=0,rowspan=2)
        #以上为默认，不要动，以下可添加图片绑定功能self.Figure.Figure.bind('<Key>',self.CommandBindFigureKey)
    def create_panel(self):
        #R1
        self.create_var('FlagReverseColor',self.back,'Boolean',False,True)
        self.ButtonR1_1=ttk.Button(self.FramePanel,text='颜色翻转',command=self.CommandButtonReverseColor)
        self.ButtonR1_1.grid(row=0,column=0,sticky='w')
        self.create_var('FlagBinary',self.back,'Boolean',False,True)
        self.ButtonR1_2=ttk.Button(self.FramePanel,text='二值化处理',command=self.CommandButtonBinary)
        self.ButtonR1_2.grid(row=0,column=1,sticky='w')
        self.create_var('ThresBinary',self.back,'Int',0,True)
        self.LER1_1=LabelEntry(self.FramePanel,'二值化阈值=',self.ThresBinary)
        self.LER1_1.grid(row=0,column=2,sticky='w')
        self.LER1_1.entry.bind('<Return>',self.CommandBindThresBinary)
        #R2
        self.create_var('XLeft',self.back,'Int',0,True)
        self.create_var('XRight',self.back,'Int',0,True)
        self.create_var('Y',self.back,'Int',0,True)
        self.create_var('LowpassFreq',self.back,'Int',50,True)
        self.LER2_1=LabelEntry(self.FramePanel,'左点X=',self.XLeft)
        self.LER2_1.grid(row=1,column=0,sticky='w')
        self.LER2_1.entry.bind('<Return>',self.CommandBindXLeft)
        self.LER2_2=LabelEntry(self.FramePanel,'右点X=',self.XRight)
        self.LER2_2.grid(row=1,column=1,sticky='w')
        self.LER2_2.entry.bind('<Return>',self.CommandBindXRight)
        self.LER2_3=LabelEntry(self.FramePanel,'Y=',self.Y)
        self.LER2_3.grid(row=1,column=2,sticky='w')
        self.LER2_3.entry.bind('<Return>',self.CommandBindY)
        self.LER2_4=LabelEntry(self.FramePanel,'低通滤波频率=',self.LowpassFreq,width=10)
        self.LER2_4.grid(row=1,column=3,sticky='w')
        self.LER2_4.entry.bind('<Return>',self.CommandBindLowpassFreq)
        #R3
        self.create_var('AngleL',self.back,'Double',0,True)
        self.create_var('AngleR',self.back,'Double',0,True)
        self.create_var('AngleM',self.back,'Double',0,True)
        self.create_var('Angle',self.back,'Double',0,True)
        LabelLabel(self.FramePanel,'左边界角=',self.AngleL,extratext='°').grid(row=2,column=0,sticky='w')
        LabelLabel(self.FramePanel,'右边界角=',self.AngleR,extratext='°').grid(row=2,column=1,sticky='w')
        LabelLabel(self.FramePanel,'中心线角=',self.AngleM,extratext='°').grid(row=2,column=2,sticky='w')
        LabelLabel(self.FramePanel,'雾化锥角=',self.Angle,extratext='°').grid(row=2,column=3,sticky='w')
        self.create_var('FlagLineAngle',self.back,'Boolean',False,True)
        self.ButtonR3=ttk.Button(self.FramePanel,text='显示锥角线',command=self.CommandButtonR3)
        self.ButtonR3.grid(row=2,column=4,sticky='we')
        #R4
        self.create_var('FigStart',self.back,'Int',0,True)
        self.create_var('FigEnd',self.back,'Int',0,True)
        self.LER4_1=LabelEntry(self.FramePanel,'起始帧：',self.FigStart)
        self.LER4_1.grid(row=3,column=0,sticky='w')
        self.LER4_1.entry.bind('<Return>',self.CommandBindFigStart)
        self.LER4_2=LabelEntry(self.FramePanel,'结束帧：',self.FigEnd)
        self.LER4_2.grid(row=3,column=1,sticky='w')
        self.LER4_2.entry.bind('<Return>',self.CommandBindFigEnd)
        ttk.Button(self.FramePanel,text='批量处理雾化锥角',command=self.CommandButtonCalcAtmAngle).grid(row=3,column=2,sticky='w')
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
    def CommandBindLowpassFreq(self,event):
        self.back.update('LowpassFreq',self.LowpassFreq.get(),False)
        self.FreshSelf()
    #R3
    def CommandButtonR3(self):
        self.back.update('FlagLineAngle',not self.FlagLineAngle.get())
        self.ButtonR3.config(text='关闭锥角线' if self.FlagLineAngle.get() else '显示锥角线')
        self.FreshSelf()
    #R4
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
        res=mul_calculate_atmangle(self.back.root.Main.generate_fdir(),self.FigStart.get(),self.FigEnd.get(),self.back.root.Main.CoreNum,settings)
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
        self.back.Fresh()
        self.Figure.Figure.change_figure(img)
        self.AF.update_data(self.back.resL[0],self.back.resL[1])
        self.BF.update_data(self.back.resR[0],self.back.resR[1])
        self.AAF.update_data(self.back.resLdiff[0],self.back.resLdiff[1])
        self.BBF.update_data(self.back.resRdiff[0],self.back.resRdiff[1])
        self.AAAF.update_data(self.back.resLdiff2[0],self.back.resLdiff2[1])
        self.BBBF.update_data(self.back.resRdiff2[0],self.back.resRdiff2[1])
        self.back.update('AngleL',65.6)
        self.back.update('AngleR',119.2)
        #R2
        # self.FrameR2=ttk.Frame(self.FramePanel)
        # self.FrameR2.pack()
        # self.create_var('FlagMinusBG',self.back,'Boolean',False,True)
        # ttk.Checkbutton(self.FrameR2,onvalue=True,offvalue=False,
        #                 variable=self.FlagMinusBG,command=self.CommandCheckButtonFlagMinusBG).pack(side='left')
        # ttk.Label(self.FrameR2,text='减背景').pack(side='left')
        # self.create_var('DirBG',self.back,'String','',True)
        # ChooseFile(self.FrameR2,'背景图片目录：',self.DirBG).pack(side='left')
        # self.create_var('BGYStart',self.back,'Int',0,True)
        # self.LER2_1=LabelEntry(self.FrameR2,'背景起始y坐标=',self.BGYStart)
        # self.LER2_1.pack(side='left')
        # self.LER2_1.entry.bind('<Return>',self.CommandBindBGYStart)
        #R3
        # self.FrameR3=ttk.Frame(self.FramePanel)
        # self.FrameR3.pack()
        # self.create_var('FlagMinusLast',self.back,'Boolean',False,True)
        # ttk.Checkbutton(self.FrameR3,onvalue=True,offvalue=False,
        #                 variable=self.FlagMinusLast,command=self.CommandCheckButtonFlagMinusLast).pack(side='left')
        # ttk.Label(self.FrameR3,text='减上一张').pack(side='left')

        # self.create_var('FigStart',self.back,'Int',0,True)
        # self.create_var('FigEnd',self.back,'Int',0,True)
        # self.LER1_1=LabelEntry(self.FrameR1,'起始帧：',self.FigStart)
        # self.LER1_1.pack(side='left')
        # self.LER1_1.entry.bind('<Return>',self.CommandBindFigStart)
        # self.LER1_2=LabelEntry(self.FrameR1,'结束帧：',self.FigEnd)
        # self.LER1_2.pack(side='left')
        # self.LER1_2.entry.bind('<Return>',self.CommandBindFigEnd)
        # ttk.Button(self.FramePanel,text='计算平均图',command=self.CommandButtonCalcAverage).pack(side='left')
    # def CommandCheckButtonFlagMinusBG(self):
    #     self.back.update('FlagMinusBG',self.FlagMinusBG.get(),False)
    # def CommandBindBGYStart(self):
    #     self.back.update('BGYStart',self.BGYStart.get(),False)
    # def CommandCheckButtonFlagMinusLast(self):
    #     self.back.update('FlagMinusLast',self.FlagMinusLast.get(),False)