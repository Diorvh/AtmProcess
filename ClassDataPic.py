import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.pylab import mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
import numpy as np
from lib_tkwidget import *
class ClassDataPic(ttk.Frame):
    def __init__(self,root,width,height,title,xdata,ydata,xname,xunit,yname,yunit):
        super().__init__(root)
        self.title=title
        self.width=width
        self.height=height
        self.xdata=np.array(xdata)
        self.ydata=np.array(ydata)
        self.xname=xname
        self.xunit=xunit
        self.yname=yname
        self.yunit=yunit
        mpl.rcParams['font.sans-serif']=['SimHei']
        mpl.rcParams['axes.unicode_minus']=False
        self.generate()
    def generate(self):
        self.create_matplotlib()
        self.print_to_canvas()
        self.create_information()
    def create_matplotlib(self):
        self.figure,self.ax=plt.subplots()
        self.ax.set(title=self.title,ylabel=self.yname,xlabel=self.xname)
        self.line,=self.ax.plot(self.xdata,self.ydata)
        self.xmin=tk.DoubleVar(self,np.min(self.xdata)*0.95)
        self.xmax=tk.DoubleVar(self,np.max(self.xdata)*1.05)
        self.ymin=tk.DoubleVar(self,np.min(self.ydata)*0.95)
        self.ymax=tk.DoubleVar(self,np.max(self.ydata)*1.05)
        self.xmin.trace_add('write',self.var_fresh)
        self.xmax.trace_add('write',self.var_fresh)
        self.ymin.trace_add('write',self.var_fresh)
        self.ymax.trace_add('write',self.var_fresh)
        self.ax.axis([self.xmin.get(),self.xmax.get(),self.ymin.get(),self.ymax.get()])
    def print_to_canvas(self):
        self.canvas=FigureCanvasTkAgg(self.figure,self)
        self.canvas.draw()
        self.canvas.get_tk_widget().config(width=self.width,height=self.height)
        self.canvas.get_tk_widget().pack()
        # toolbar=NavigationToolbar2Tk(self.canvas,self)
        # toolbar.uupdate()
        # self.canvas._tkcanvas.pack(side=tk.TOP,fill=tk.BOTH,expand=1)
    def create_information(self):
        self.FrameR2=ttk.Frame(self)
        self.FrameR2.pack()
        ttk.Label(self.FrameR2,text=self.xname+':').pack(side='left')
        self.Xvalue=tk.IntVar(self,1)
        self.Xvalue.trace_add('write',self.update_Yvalue)
        ttk.Entry(self.FrameR2,textvariable=self.Xvalue).pack(side='left')
        ttk.Label(self.FrameR2,text=self.xunit).pack(side='left')
        ttk.Button(self.FrameR2,text='+1',command=self.CommandButtonUp1,width=3).pack(side='left')
        ttk.Button(self.FrameR2,text='-1',command=self.CommandButtonDown1,width=3).pack(side='left')
        ttk.Label(self.FrameR2,text=self.yname+':').pack(side='left')
        self.Yvalue=tk.DoubleVar(self,0)
        ttk.Label(self.FrameR2,textvariable=self.Yvalue).pack(side='left')
        ttk.Label(self.FrameR2,text=self.yunit).pack(side='left')
        self.FrameR3=ttk.Frame(self)
        self.FrameR3.pack()
        LabelEntry(self.FrameR3,self.yname+'-max',self.ymax).pack(side='left')
        LabelEntry(self.FrameR3,self.yname+'-min',self.ymin).pack(side='left')
        LabelEntry(self.FrameR3,self.xname+'-min',self.xmin).pack(side='left')
        LabelEntry(self.FrameR3,self.xname+'-max',self.xmax).pack(side='left')
    def CommandButtonUp1(self):
        self.Xvalue.set(self.Xvalue.get()+1)
    def CommandButtonDown1(self):
        self.Xvalue.set(self.Xvalue.get()-1)
    def update_Yvalue(self,*args):
        try:
            index=np.where(self.xdata==self.Xvalue.get())[0][0]
            self.Yvalue.set(self.ydata[index])
        except:
            pass
    def fresh(self):
        self.line.set_data(self.xdata,self.ydata)
        self.xmin.set(np.min(self.xdata)*0.95)
        self.xmax.set(np.max(self.xdata)*1.05)
        self.ymin.set(np.min(self.ydata)*0.95)
        self.ymax.set(np.max(self.ydata)*1.05)
        self.ax.axis([self.xmin.get(),self.xmax.get(),self.ymin.get(),self.ymax.get()])
        self.canvas.draw_idle()
    def var_fresh(self,*args):
        self.fresh()
if __name__=='__main__':
    root=tk.Tk()
    xdata=range(1,101)
    ydata=range(101,201)
    Pic=ClassDataPic(root,1000,200,'test',xdata,ydata,'x','xunit','y','yunit')
    Pic.pack()
    ttk.Button(Pic,text='update',command=Pic.fresh).pack()
    root.mainloop()