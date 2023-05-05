# import sys
# sys.path.append(r'D:\Files\Codes\Python\lib\lib_openpyxl')
import tkinter as tk
from tkinter import ttk
from lib_tkwidget import *
from FrameChoosePic import *
from database import *
import os
#依赖库：pip install numpy TinyDB matplotlib openpyxl
class Main(ttk.Frame):
    def __init__(self,master):
        super().__init__(master)
        self.db=DB()
        self.FramePanel=ttk.Frame(self,padding=5,relief='sunken')
        self.FramePanel.grid(row=0,column=0,sticky='NSWE')
        self.create_panel()
        self.FrameChoosePic=FrameChoosePic(self)
        self.FrameChoosePic.grid(row=1,column=0)
        self.db.load()
    def create_panel(self):
        #R1
        self.FrameR1=ttk.Frame(self.FramePanel)
        self.FrameR1.pack(fill='x')
        self.DirData=tk.StringVar(self)
        self.db.Main.DirData_front=self.DirData
        ttk.Label(self.FrameR1,text='数据文件夹：').pack(side='left')
        ttk.Label(self.FrameR1,textvariable=self.DirData,width=50).pack(side='left')
        ttk.Button(self.FrameR1,text='选择文件',command=self.CommandButtonChooseFile).pack(side='left')
        #R2
        self.FrameR2=ttk.Frame(self.FramePanel)
        self.FrameR2.pack(fill='x')
        self.ExpNo=tk.IntVar(self,1)
        self.db.Main.ExpNo_front=self.ExpNo
        self.LER2=LabelEntry(self.FrameR2,'实验编号',self.ExpNo)
        self.LER2.pack(side='left')
        self.LER2.entry.bind('<Return>',self.ExpNoFresh)
        ttk.Button(self.FrameR2,text='+1',width=2,command=self.CommandButtonExpNoInc).pack(side='left')
        ttk.Button(self.FrameR2,text='-1',width=2,command=self.CommandButtonExpNoDec).pack(side='left')
        # ttk.Button(self.FrameR2,text='刷新',width=4,command=self.Fresh).pack(side='left')
        #R3
        self.FrameR3=ttk.Frame(self.FramePanel)
        self.FrameR3.pack(fill='x')
        self.FDirRes=tk.StringVar()
        self.db.Main.FDirRes_front=self.FDirRes
        ttk.Label(self.FrameR3,text='结果文件：').pack(side='left')
        ttk.Label(self.FrameR3,textvariable=self.FDirRes,width=50).pack(side='left')
        ttk.Button(self.FrameR3,text='选择文件',command=self.CommandButtonChooseFile2).pack(side='left')
    def CommandButtonChooseFile(self):
        self.DirData.set(filedialog.askdirectory(title='选择文件'))
        self.db.Main.update('DirData',self.DirData.get(),False)
    def CommandButtonExpNoInc(self):
        self.ExpNo.set(self.ExpNo.get()+1)
        self.ExpNoFresh()
    def CommandButtonExpNoDec(self):
        self.ExpNo.set(self.ExpNo.get()-1)
        self.ExpNoFresh()
    def ExpNoFresh(self,*args):
        self.db.Main.update('ExpNo',self.ExpNo.get(),False)
        filename=os.listdir()
        if '实验编号'+str(self.ExpNo.get()) in filename:
            self.Fresh()
    def CommandButtonChooseFile2(self):
        self.FDirRes.set(filedialog.askopenfilename(title='选择文件'))
        self.db.Main.update('FDirRes',self.FDirRes.get(),False)
    def Fresh(self):
        self.FrameChoosePic.Fresh()
def close_window():
    App.db.save()
    root.quit()
    root.destroy()
if __name__=='__main__':
    root=tk.Tk()
    App=Main(root)
    App.pack()
    root.protocol("WM_DELETE_WINDOW",close_window)
    root.mainloop()