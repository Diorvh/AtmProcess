import sys
sys.path.append(r'D:\Files\Codes\Python\lib\lib_openpyxl')
import tkinter as tk
from tkinter import ttk
from lib_tkwidget import *
from FrameProcess import *
import openpyxl
class FrameChoosePic(ttk.Frame):
    def __init__(self,master):
        self.root=master
        super().__init__(self.root,padding=5,relief='sunken')
        # self.FPS=40000
        # self.FigureNameList=[]
        # self.res={}
        self.create_panel()
        self.NotebookProcess=ttk.Notebook(self)
        self.NotebookProcess.pack()
        #Notebook界面
        # self.MeasureSheet=ClassMeasureSheet(self)
        # self.NotebookProcess.add(self.MeasureSheet,text='液膜测量')
    def create_panel(self):
        self.FramePanel=ttk.Frame(self)
        self.FramePanel.pack()
        #R1
        self.Decimate=tk.IntVar(self)
        LabelEntry(self.FramePanel,text='Decimate=',var=self.Decimate).grid(row=0,column=0,sticky='W')
        ttk.Button(self.FramePanel,text='保存',command=self.CommandButtonSave).grid(row=0,column=1,sticky='W')
        #R2
        self.FrameR2C1=ttk.Frame(self.FramePanel)
        self.FrameR2C1.grid(row=1,column=0,sticky='W')
        self.FigNameStart=tk.IntVar(self)
        self.FigNameEnd=tk.IntVar(self)
        ttk.Label(self.FrameR2C1,text='图片范围：').pack(side='left')
        ttk.Label(self.FrameR2C1,textvariable=self.FigNameStart,width=5).pack(side='left')
        ttk.Label(self.FrameR2C1,text='-').pack(side='left')
        ttk.Label(self.FrameR2C1,textvariable=self.FigNameEnd,width=5).pack(side='left')
        self.FrameR2C2=ttk.Frame(self.FramePanel)
        self.FrameR2C2.grid(row=1,column=1,sticky='W')
        self.CurrentName=tk.IntVar(self)
        ttk.Label(self.FrameR2C2,text='当前序号：').pack(side='left')
        ttk.Entry(self.FrameR2C2,textvariable=self.CurrentName,width=5).pack(side='left')
        ttk.Button(self.FrameR2C2,text='+1',width=2,command=self.CommandButtonNameInc).pack(side='left')
        ttk.Button(self.FrameR2C2,text='-1',width=2,command=self.CommandButtonNameDec).pack(side='left')
        #R3
        self.ImpactX=tk.IntVar(self)
        self.ImpactY=tk.IntVar(self)
        self.FrameR3C1=ttk.Frame(self.FramePanel)
        self.FrameR3C1.grid(row=2,column=0,sticky='W')
        ttk.Label(self.FrameR3C1,text='基点：').pack(side='left')
        ttk.Entry(self.FrameR3C1,textvariable=self.ImpactX,width=4).pack(side='left')
        ttk.Label(self.FrameR3C1,text=',').pack(side='left')
        ttk.Entry(self.FrameR3C1,textvariable=self.ImpactY,width=4).pack(side='left')
        self.PixSize=tk.DoubleVar(self)
        LabelEntry(self.FramePanel,'像素尺寸=',self.PixSize,width=6,extratext='um').grid(row=2,column=1,sticky='W')
    def CommandButtonNameInc(self):
        pass# self.res.append([self.CurrentName.get()]+self.MeasureSheet.get_res())
        # if self.CurrentName.get()<self.FigNameEnd.get():
        #     self.CurrentName.set(self.FigureNameList[self.FigureNameList.index(self.CurrentName.get())+1])
        # self.MeasureSheet.update_figure()
    def CommandButtonNameDec(self):
        pass# if self.CurrentName.get()>self.FigNameStart.get():
        #     self.CurrentName.set(self.FigureNameList[self.FigureNameList.index(self.CurrentName.get())-1])
        # self.MeasureSheet.update_figure()
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
if __name__=='__main__':
    root=tk.Tk()
    App=FrameChoosePic(root)
    App.pack()
    # root.protocol("WM_DELETE_WINDOW",close_window)
    root.mainloop()