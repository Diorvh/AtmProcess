import tkinter as tk
from tkinter import ttk
from database import db
from lib_tkwidget import *
from ClassProcess import ClassProcess
import matplotlib.pyplot as plt
import os 
class QProcess(ttk.Frame):
    def __init__(self,master):
        super().__init__(master)
        self.create_panel()
        self.Process0=ClassProcess(self,name='整体',interval=True)
        self.Process0.grid(row=1,column=0)
        self.Process1=ClassProcess(self,name='实验段',interval=[0,3000])
        self.Process1.grid(row=1,column=1)
        self.Process2=ClassProcess(self,name='计算cd',interval=[6000,7000])
        self.Process2.grid(row=1,column=2)
    def create_panel(self):
        self.FramePanel=ttk.Frame(self,padding=5,relief='sunken')
        self.FramePanel.grid(row=0,column=0,columnspan=3)
        self.new_var('DirData')
        ChooseFile(self.FramePanel,'数据文件夹：',self.DirData,type='Dir',width=100).pack()
        self.FrameR1=ttk.Frame(self.FramePanel)
        self.FrameR1.pack(fill='x')
        self.new_var('ExpNo','Int')
        LabelEntry(self.FrameR1,'实验编号',self.ExpNo).pack(side='left')
        ttk.Button(self.FrameR1,text='+1',width=2,command=self.CommandButtonExpNoInc).pack(side='left')
        ttk.Button(self.FrameR1,text='-1',width=2,command=self.CommandButtonExpNoDec).pack(side='left')
        self.new_var('FDirData')
        self.new_var('FDirRes')
        ttk.Button(self.FrameR1,text='读取',width=5,command=self.CommandButtonReadFDir).pack(side='left')
        ChooseFile(self.FramePanel,'数据文件',self.FDirData,width=100).pack()
        ChooseFile(self.FramePanel,'结果文件',self.FDirRes,width=100).pack()
    def CommandButtonExpNoInc(self):
        self.ExpNo.set(self.ExpNo.get()+1)
        self.CommandButtonReadFDir()
        if self.wfile!='':
            self.fresh_data()
    def CommandButtonExpNoDec(self):
        self.ExpNo.set(self.ExpNo.get()-1)
        self.CommandButtonReadFDir()
        if self.wfile!='':
            self.fresh_data()
    def CommandButtonReadFDir(self):
        self.wfile=''
        for filename in os.listdir(self.DirData.get()):
            if '实验编号'+str(self.ExpNo.get())+'.csv' in filename:
                self.wfile=filename
        self.FDirData.set(self.DirData.get()+'/'+self.wfile)
    def fresh_data(self):
        pass
    def Update(self,name,index,mode):#更新数据库
        try:
            db.update(name,getattr(self,name).get())
        except:
            pass
    def new_var(self,name,type='String'):#后端，创建变量并与数据库同步
        setattr(self,name,getattr(tk,type+'Var')(name=name,value=db.get(name)))#后端
        getattr(self,name).trace_add('write',self.Update)#变量变动就马上更新数据库
def close_window():
    plt.close()
    root.quit()
    root.destroy()
if __name__=='__main__':
    root=tk.Tk()
    App=QProcess(root)
    App.pack()
    root.protocol("WM_DELETE_WINDOW",close_window)
    root.mainloop()