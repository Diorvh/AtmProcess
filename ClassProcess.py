import tkinter as tk
from tkinter import ttk,filedialog
from lib_tkwidget import *
from ClassDataPic import *
from copy import deepcopy
class ClassProcess(ttk.Frame):
    def __init__(self,master,name='区间1：',interval=[0,1000],data=None,digit=5,tmap=lambda x:x+501):
        super().__init__(master,padding=5,relief='sunken')
        self.name=name
        self.tmap=tmap#从时间映射到data的行序号（不需要-1）
        self.digit=digit
        self.get_data(data)
        self.get_interval(interval)
        self.create_param()
        self.fresh_data()
        self.create_Panel()
    def get_data(self,data):
        if type(data)==type(None):
            self.data=np.genfromtxt('23_03_12_20_21_38_实验编号85.csv', delimiter=',')
        else:
            self.data=data
        self.informrows=7
        self.inform=self.data[:self.informrows]
        self.data=self.data[self.informrows:]
        self.errrow=3
    def get_interval(self,interval):
        if interval==True:
            self.IntL=tk.IntVar(self,self.data[0,0])
            self.IntR=tk.IntVar(self,self.data[-1,0])
        else:
            self.IntL=tk.IntVar(self,interval[0])
            self.IntR=tk.IntVar(self,interval[1])
    def create_param(self):#初始化参数
        self.width=400
        self.height=200
        self.VarName=['DP','Q','Pc']
        self.VarName_unit=['MPa','g/s','MPa']
        self.VarName_row_col=[(0,1),(1,1),(2,1)]
        self.VarName_datacol=np.array([4,5,10])-1#写入从1开始的下标列数
        for j,i in enumerate(self.VarName):
            setattr(self,'Data'+i,tk.DoubleVar(self))
            setattr(self,'DataD'+i,tk.DoubleVar(self))
            setattr(self,'DataDErrP'+i,tk.DoubleVar(self))
            setattr(self,'DataPic'+i,ClassDataPic(self,self.width,self.height,i,[1],[1],'时间','ms',i,self.VarName_unit[j]))
    def create_Panel(self):
        self.FrameR0=ttk.Frame(self)
        self.FrameR0.pack()
        ttk.Label(self.FrameR0,text=self.name).pack(side='left')
        # ttk.Button(self.FrameR0,text='刷新',width=5,command=self.fresh_data).pack(side='left')
        self.FrameR1=ttk.Frame(self)
        self.FrameR1.pack()
        ttk.Label(self.FrameR1,text='时间区间：').pack(side='left')
        self.Entry1=ttk.Entry(self.FrameR1,textvariable=self.IntL,width=5)
        self.Entry1.pack(side='left')
        self.Entry1.bind('<Return>',self.bind_fresh_data)
        ttk.Label(self.FrameR1,text='ms').pack(side='left')
        ttk.Button(self.FrameR1,text='+1',width=2,command=self.CommandButtonIntLInc).pack(side='left')
        ttk.Button(self.FrameR1,text='-1',width=2,command=self.CommandButtonIntLDec).pack(side='left')
        ttk.Label(self.FrameR1,text='----').pack(side='left')
        self.Entry2=ttk.Entry(self.FrameR1,textvariable=self.IntR,width=5)
        self.Entry2.pack(side='left')
        self.Entry2.bind('<Return>',self.bind_fresh_data)
        ttk.Label(self.FrameR1,text='ms').pack(side='left')
        ttk.Button(self.FrameR1,text='+1',width=2,command=self.CommandButtonIntRInc).pack(side='left')
        ttk.Button(self.FrameR1,text='-1',width=2,command=self.CommandButtonIntRDec).pack(side='left')
        self.FrameR2=ttk.Frame(self)
        self.FrameR2.pack()
        ttk.Label(self.FrameR2,text='结果：').grid(row=0,column=0)
        for j,i in enumerate(self.VarName):
            setattr(self,'FrameData'+i,FrameData(self.FrameR2,i,getattr(self,'Data'+i),getattr(self,'DataD'+i),getattr(self,'DataDErrP'+i)))
            getattr(self,'FrameData'+i).grid(row=self.VarName_row_col[j][0],column=self.VarName_row_col[j][1])
        self.FrameR4=ttk.Frame(self)
        self.FrameR4.pack()
        for i in self.VarName:
            getattr(self,'DataPic'+i).pack()
    def fresh_data(self):
        rrange=self.tmap(self.IntL.get())-1,self.tmap(self.IntR.get())
        self.xdata=self.data[rrange[0]:rrange[1],0]
        for j,i in enumerate(self.VarName):
            cache=self.data[rrange[0]:rrange[1],self.VarName_datacol[j]]
            setattr(self,'Curve'+i,cache)
            getattr(self,'Data'+i).set(np.round((np.average(cache)),self.digit))
            getattr(self,'DataD'+i).set(np.round((np.ptp(cache)/np.average(cache)*100/2),self.digit))
            ErrP=(self.inform[self.errrow,self.VarName_datacol[j]]-self.inform[self.errrow-1,self.VarName_datacol[j]])*0.001
            getattr(self,'DataDErrP'+i).set(np.round(((np.ptp(cache)+ErrP)/np.average(cache)*100/2),self.digit))
            getattr(self,'DataPic'+i).xdata=deepcopy(self.xdata)
            getattr(self,'DataPic'+i).ydata=deepcopy(cache)
            getattr(self,'DataPic'+i).fresh()
        self.DataDErrPQ.set(np.round(min(0.5,0.056/self.DataQ.get()*100),self.digit))
    def bind_fresh_data(self,event):
        self.fresh_data()
    def CommandButtonIntLInc(self):
        self.IntL.set(self.IntL.get()+1)
        self.fresh_data()
    def CommandButtonIntLDec(self):
        self.IntL.set(self.IntL.get()-1)
        self.fresh_data()
    def CommandButtonIntRInc(self):
        self.IntR.set(self.IntR.get()+1)
        self.fresh_data()
    def CommandButtonIntRDec(self):
        self.IntR.set(self.IntR.get()-1)
        self.fresh_data()
if __name__=='__main__':
    root=tk.Tk()
    ClassProcess(root).pack()
    root.mainloop()