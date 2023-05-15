import sys,os
sys.path.append(os.getcwd())
import tkinter as tk
from tkinter import ttk
from FrameChoosePic import *
from database import *
from lib.lib_tkwidget import *
from lib.BaseClass import *
from lib.ScrollableFrame import *
#依赖库：pip install numpy TinyDB matplotlib openpyxl
class Base:
    def __init__(self,father:tk.Tk):
        self.father=father
        self.father.state('zoomed')
        self.MainFrame=ScrollableFrame(self.father)
        self.MainFrame.pack(fill='both',expand=True)
        self.Main=Main(self.MainFrame.scrollable_frame)
        self.Main.pack()
class Main(BaseFrame):
    def __init__(self,father):
        super().__init__(father)
        self.db=DB()
        self.back=self.db.Main
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
        self.create_var('DirData',self.back,init_value='',FlagSave=True)
        ttk.Label(self.FrameR1,text='数据文件夹：').pack(side='left')
        ttk.Label(self.FrameR1,textvariable=self.DirData,width=50).pack(side='left')
        ttk.Button(self.FrameR1,text='选择文件',command=self.CommandButtonChooseFile).pack(side='left')
        #R2
        self.FrameR2=ttk.Frame(self.FramePanel)
        self.FrameR2.pack(fill='x')
        self.create_var('ExpNo',self.back,type='Int',init_value=0,FlagSave=True)
        LE=LabelEntry(self.FrameR2,'实验编号',self.ExpNo)
        LE.pack(side='left')
        LE.entry.bind('<Return>',self.CommandBindExpNo)
        ttk.Button(self.FrameR2,text='+1',width=2,command=self.CommandButtonExpNoInc).pack(side='left')
        ttk.Button(self.FrameR2,text='-1',width=2,command=self.CommandButtonExpNoDec).pack(side='left')
        # ttk.Button(self.FrameR2,text='刷新',width=4,command=self.Fresh).pack(side='left')
        #R3
        self.FrameR3=ttk.Frame(self.FramePanel)
        self.FrameR3.pack(fill='x')
        self.create_var('FDirRes',self.back,init_value='',FlagSave=True)
        ttk.Label(self.FrameR3,text='结果文件：').pack(side='left')
        ttk.Label(self.FrameR3,textvariable=self.FDirRes,width=50).pack(side='left')
        ttk.Button(self.FrameR3,text='选择文件',command=self.CommandButtonChooseFile2).pack(side='left')
    def CommandButtonChooseFile(self):
        self.back.update('DirData',filedialog.askdirectory(title='选择文件'))
    def ChangeExpNo(self):
        self.Fresh()
        self.FrameChoosePic.back.data=[]
        self.FrameChoosePic.Table.update_table(self.FrameChoosePic.back.data[:])
    def CommandButtonExpNoInc(self):
        filename=os.listdir(self.DirData.get())
        if '实验编号'+str(self.ExpNo.get()+1) in filename:
            self.back.update('ExpNo',self.ExpNo.get()+1)
            self.ChangeExpNo()
    def CommandButtonExpNoDec(self):
        filename=os.listdir(self.DirData.get())
        if '实验编号'+str(self.ExpNo.get()-1) in filename:
            self.back.update('ExpNo',self.ExpNo.get()-1)
            self.ChangeExpNo()
    def CommandBindExpNo(self,*args):
        filename=os.listdir(self.DirData.get())
        if '实验编号'+str(self.ExpNo.get()) in filename:
            self.back.update('ExpNo',self.ExpNo.get())
            self.ChangeExpNo()
    def CommandButtonChooseFile2(self):
        self.back.update('FDirRes',filedialog.askopenfilename(title='选择文件'))
    def Fresh(self):
        self.back.FrameChoosePic.Fresh()
        self.FrameChoosePic.Fresh()
def close_window():
    App.Main.db.save()
    root.quit()
    root.destroy()
if __name__=='__main__':
    root=tk.Tk()
    App=Base(root)
    root.protocol("WM_DELETE_WINDOW",close_window)
    root.mainloop()