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
        self.create_var('CoreNum',self.back,'Int',0,True)
        LE1=LabelEntry(self.FrameR1,'并行进程数',self.CoreNum)
        LE1.pack(side='left')
        LE1.entry.bind('<Return>',self.CommandBindCoreNum)
        #R2
        self.FrameR2=ttk.Frame(self.FramePanel)
        self.FrameR2.pack(fill='x')
        self.create_var('DirData',self.back,init_value='',FlagSave=True)
        ttk.Label(self.FrameR2,text='数据文件夹：').pack(side='left')
        ttk.Label(self.FrameR2,textvariable=self.DirData,width=50).pack(side='left')
        ttk.Button(self.FrameR2,text='选择文件',command=self.CommandButtonChooseFile).pack(side='left')
        self.create_var('ExpNo',self.back,type='Int',init_value=0,FlagSave=True)
        LE2=LabelEntry(self.FrameR2,'实验编号',self.ExpNo)
        LE2.pack(side='left')
        LE2.entry.bind('<Return>',self.CommandBindExpNo)
        ttk.Button(self.FrameR2,text='+1',width=2,command=self.CommandButtonExpNoInc).pack(side='left')
        ttk.Button(self.FrameR2,text='-1',width=2,command=self.CommandButtonExpNoDec).pack(side='left')
        self.create_var('FlagOther',self.back,type='Boolean',init_value=False)
        ttk.Checkbutton(self.FrameR2,onvalue=True,offvalue=False,
                        variable=self.FlagOther,command=self.CommandCheckButtonOther).pack(side='left')
        self.create_var('Other',self.back,type='String',init_value='',FlagSave=True)
        LE2=LabelEntry(self.FrameR2,'其他文件夹名称',self.Other)
        LE2.pack(side='left')
        LE2.entry.bind('<Return>',self.CommandBindOther)
        ttk.Button(self.FrameR2,text='刷新',width=4,command=self.Fresh).pack(side='left')
        #R3
        self.FrameR3=ttk.Frame(self.FramePanel)
        self.FrameR3.pack(fill='x')
        self.create_var('FlagDirect',self.back,type='Boolean',init_value=False)
        ttk.Checkbutton(self.FrameR3,text='直接选择图片',onvalue=True,offvalue=False,
                        variable=self.FlagDirect,command=self.CommandCheckButtonDirect).pack(side='left')
        self.create_var('DirDirect',self.back,init_value='',FlagSave=True)
        ttk.Entry(self.FrameR3,textvariable=self.DirDirect,width=50).pack(side='left')
        ttk.Button(self.FrameR3,text='选择图片',command=self.CommandButtonChooseFile2).pack(side='left')
        self.create_var('ImageLabel',self.back,init_value='',FlagSave=True)
        self.LER3=LabelEntry(self.FrameR3,text='图片标识',var=self.ImageLabel)
        self.LER3.pack(side='left')
        self.LER3.entry.bind('<Return>',self.CommandBindImageLabel)
        #R4
        self.FrameR4=ttk.Frame(self.FramePanel)
        self.FrameR4.pack(fill='x')
        self.create_var('FDirRes',self.back,init_value='',FlagSave=True)
        ttk.Label(self.FrameR4,text='结果文件：').pack(side='left')
        ttk.Label(self.FrameR4,textvariable=self.FDirRes,width=50).pack(side='left')
        ttk.Button(self.FrameR4,text='选择文件',command=self.CommandButtonChooseFile3).pack(side='left')
    def CommandBindCoreNum(self,event):
        self.back.update('CoreNum',self.CoreNum.get(),False)

    def CommandButtonChooseFile(self):
        self.back.update('DirData',filedialog.askdirectory(title='选择文件'))
    def CommandButtonExpNoInc(self):
        filename=os.listdir(self.DirData.get())
        if '实验编号'+str(self.ExpNo.get()+1) in filename:
            self.back.update('ExpNo',self.ExpNo.get()+1)
            self.Fresh()
    def CommandButtonExpNoDec(self):
        filename=os.listdir(self.DirData.get())
        if '实验编号'+str(self.ExpNo.get()-1) in filename:
            self.back.update('ExpNo',self.ExpNo.get()-1)
            self.Fresh()
    def CommandBindExpNo(self,*args):
        filename=os.listdir(self.DirData.get())
        if '实验编号'+str(self.ExpNo.get()) in filename:
            self.back.update('ExpNo',self.ExpNo.get())
            self.Fresh()
    def CommandCheckButtonOther(self):
        self.back.update('FlagOther',self.FlagOther.get(),False)
    def CommandBindOther(self,event):
        self.back.update('Other',self.Other.get())
        self.Fresh()
    
    def CommandCheckButtonDirect(self):
        self.back.update('FlagDirect',self.FlagDirect.get(),False)
    def CommandButtonChooseFile2(self):
        self.back.update('DirDirect',filedialog.askopenfilename(title='选择图像'))
        self.Fresh()
    def CommandBindImageLabel(self,event):
        self.back.update('ImageLabel',self.ImageLabel.get(),False)

    def CommandButtonChooseFile3(self):
        self.back.update('FDirRes',filedialog.askopenfilename(title='选择文件'))
    def Fresh(self):
        self.back.FrameChoosePic.Fresh()
        self.FrameChoosePic.Fresh()
        self.FrameChoosePic.back.data=[]
def close_window():
    App.Main.db.save()
    root.quit()
    root.destroy()
if __name__=='__main__':
    root=tk.Tk()
    App=Base(root)
    root.protocol("WM_DELETE_WINDOW",close_window)
    root.mainloop()