import sys
sys.path.append(r'D:\Files\Codes\Python\lib\lib_openpyxl')
import tkinter as tk
from tkinter import ttk
from lib_tkwidget import *
from ClassMeasureSheet import *
import openpyxl,os
from BaseClass import *
class FrameChoosePic(BaseFrame):
    def __init__(self,master):
        self.father=master
        self.db=master.db
        self.back=self.db.Main.FrameChoosePic
        super().__init__(self.father,padding=5,relief='sunken')
        self.FramePanel=ttk.Frame(self)
        self.FramePanel.grid(row=0,column=0)
        self.create_panel()
        self.NotebookProcess=ttk.Notebook(self)
        self.NotebookProcess.grid(row=1,column=0)
        self.Table=TableFrame(self,['图名称','帧数','左线','右线','上线','下线','宽度/mm','长度/mm'])#TODO:调整默认宽度,切换液面就切换标题（绑定到每个子类）
        self.Table.grid(row=0,column=1,rowspan=2,sticky='nw')
        #Notebook界面
        self.MeasureSheet=ClassMeasureSheet(self)
        self.NotebookProcess.add(self.MeasureSheet,text='液膜测量')
    def create_panel(self):
        #R1
        self.create_var('Decimate',self.back,type='Int',init_value=0,FlagSave=True)
        self.LER1=LabelEntry(self.FramePanel,text='Decimate=',var=self.Decimate)
        self.LER1.grid(row=0,column=0,sticky='W')
        self.LER1.entry.bind('<Return>',self.CommandBindDecimate)
        ttk.Button(self.FramePanel,text='保存本组数据序列',command=self.CommandButtonSave).grid(row=0,column=1,sticky='W')
        #R2
        self.FrameR2C1=ttk.Frame(self.FramePanel)
        self.FrameR2C1.grid(row=1,column=0,sticky='W')
        self.create_var('FigNameStart',self.back,type='Int',init_value=0,FlagSave=True)
        self.create_var('FigNameEnd',self.back,type='Int',init_value=0,FlagSave=True)
        ttk.Label(self.FrameR2C1,text='图片范围：').pack(side='left')
        ttk.Label(self.FrameR2C1,textvariable=self.FigNameStart,width=5).pack(side='left')
        ttk.Label(self.FrameR2C1,text='-').pack(side='left')
        ttk.Label(self.FrameR2C1,textvariable=self.FigNameEnd,width=5).pack(side='left')
        self.FrameR2C2=ttk.Frame(self.FramePanel)
        self.FrameR2C2.grid(row=1,column=1,sticky='W')
        self.create_var('FigName',self.back,type='Int',init_value=0,FlagSave=True)
        ttk.Label(self.FrameR2C2,text='当前序号：').pack(side='left')
        Entry=ttk.Entry(self.FrameR2C2,textvariable=self.FigName,width=5)
        Entry.pack(side='left')
        Entry.bind('<Return>',self.CommandBindFigName)
        ttk.Button(self.FrameR2C2,text='+1',width=2,command=self.CommandButtonFigNameInc).pack(side='left')
        ttk.Button(self.FrameR2C2,text='-1',width=2,command=self.CommandButtonFigNameDec).pack(side='left')
        #R3
        self.create_var('ImpactX',self.back,type='Int',init_value=0,FlagSave=True)
        self.create_var('ImpactY',self.back,type='Int',init_value=0,FlagSave=True)
        self.FrameR3C1=ttk.Frame(self.FramePanel)
        self.FrameR3C1.grid(row=2,column=0,sticky='W')
        ttk.Label(self.FrameR3C1,text='基点：').pack(side='left')
        Entry=ttk.Entry(self.FrameR3C1,textvariable=self.ImpactX,width=4)
        Entry.pack(side='left')
        Entry.bind('<Return>',self.CommandBindImpactXY)
        ttk.Label(self.FrameR3C1,text=',').pack(side='left')
        Entry=ttk.Entry(self.FrameR3C1,textvariable=self.ImpactY,width=4)
        Entry.pack(side='left')
        Entry.bind('<Return>',self.CommandBindImpactXY)
        self.create_var('PixSize',self.back,type='Double',init_value=0,FlagSave=True)
        LE=LabelEntry(self.FramePanel,'像素尺寸=',self.PixSize,width=6,extratext='um/pix')
        LE.grid(row=2,column=1,sticky='W')
        LE.entry.bind('<Return>',self.CommandBindPixSize)
    def CommandBindDecimate(self,*args):
        self.back.update('Decimate',self.Decimate.get(),False)
    def CommandButtonFigNameInc(self):
        self.back.update('FigName',self.FigName.get()+1)
        self.FigNameFresh()
    def CommandButtonFigNameDec(self):
        self.back.update('FigName',self.FigName.get()-1)
        self.FigNameFresh()
    def CommandBindFigName(self,*args):
        self.back.update('FigName',self.FigName.get())
        self.FigNameFresh()
    def FigNameFresh(self):
        if self.FigName.get() in self.back.get('FigureNameList'):
            self.Fresh()
    def CommandBindImpactXY(self,*args):
        self.back.update('ImpactX',self.ImpactX.get(),False)
        self.back.update('ImpactY',self.ImpactY.get(),False)
        #后端修改
        self.Fresh()
    def CommandBindPixSize(self,*args):
        self.back.update('PixSize',self.PixSize.get(),False)
        self.Fresh()
    def CommandButtonSave(self):
        pass
        '''
        #TODO:ddd
        #data=['初始室压',p_0,'罐初始压力',pT_0,'路初始压力',pP_0,'室压',p,'罐压力',pT,'路压力',pP,'有效路压力',pPeff,'流量',Q,'实验段有效路压力',pexpeff]
        wb_target=openpyxl.load_workbook(self.master.FDirRes.get())
        ws_target=wb_target.active
        for i in range(1,ws_target.max_column+1):
            if ws_target.cell(row=self.master.ExpNo.get()+3,column=i).value=='雾化锥角':
                ws_target.cell(self.master.ExpNo.get()+3,i,np.average(np.array(self.res)[:,0]))
            if 'ExpIntStart' == ws_target.cell(row=2,column=i).value:
                ws_target.cell(self.ExpNo.get()+3,i,self.Process[1].IntL.get())
                ws_target.cell(self.ExpNo.get()+3,i+1,self.Process[1].IntR.get())
            if 'CdIntStart' == ws_target.cell(row=2,column=i).value:
                ws_target.cell(self.ExpNo.get()+3,i,self.Process[2].IntL.get())
                ws_target.cell(self.ExpNo.get()+3,i+1,self.Process[2].IntR.get())
        wb_target.save(self.master.DirData.get()+r'/')
        '''
    def Fresh(self):
        self.MeasureSheet.FreshSelf()#改为刷新当前
if __name__=='__main__':
    root=tk.Tk()
    App=FrameChoosePic(root)
    App.pack()
    # root.protocol("WM_DELETE_WINDOW",close_window)
    root.mainloop()