import sys
sys.path.append(r'D:\Files\Codes\Python\lib\lib_openpyxl')
import tkinter as tk
from tkinter import ttk
from lib_tkwidget import *
import os
import numpy as np
from FrameChoosePic import *
from copy import deepcopy
#依赖库：pip install numpy TinyDB matplotlib openpyxl
class QProcess(ttk.Frame):
    def __init__(self,master):
        super().__init__(master)
        self.create_panel()
        self.FrameChoosePic=FrameChoosePic(self)
        self.FrameChoosePic.grid(row=1,column=0)
    def create_panel(self):
        self.FramePanel=ttk.Frame(self,padding=5,relief='sunken')
        self.FramePanel.grid(row=0,column=0,sticky='NSWE')
        #R1
        self.DirData=tk.StringVar(self)
        ChooseFile(self.FramePanel,'数据文件夹：',self.DirData,type='Dir',width=50).pack()
        #R2
        self.FrameR2=ttk.Frame(self.FramePanel)
        self.FrameR2.pack(fill='x')
        self.ExpNo=tk.IntVar(self,1)
        LabelEntry(self.FrameR2,'实验编号',self.ExpNo).pack(side='left')
        ttk.Button(self.FrameR2,text='+1',width=2,command=self.CommandButtonExpNoInc).pack(side='left')
        ttk.Button(self.FrameR2,text='-1',width=2,command=self.CommandButtonExpNoDec).pack(side='left')
        ttk.Button(self.FrameR2,text='刷新',width=4,command=self.Fresh).pack(side='left')
        #R3
        self.FDirRes=tk.StringVar()
        ChooseFile(self.FramePanel,'结果文件：',self.FDirRes,width=50).pack()
    def CommandButtonExpNoInc(self):
        pass
    def CommandButtonExpNoDec(self):
        pass
    def Fresh(self):
        pass
# def close_window():
#     plt.close()
#     root.quit()
#     root.destroy()
if __name__=='__main__':
    root=tk.Tk()
    App=QProcess(root)
    App.pack()
    # root.protocol("WM_DELETE_WINDOW",close_window)
    root.mainloop()