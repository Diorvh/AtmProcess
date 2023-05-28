import tkinter as tk
from tkinter import ttk
import cv2 as cv
from PIL import ImageTk,Image
import numpy as np
from lib.BaseClass import *
from lib.lib_tkwidget import *
class ClassFigure(ttk.Label):
    def __init__(self,father):
        self.father=father
        self.back=self.father.back
        super().__init__(self.father,takefocus=True)
        #初始化
        self.change_figure(np.random.randint(0,256,size=(640,704),dtype='uint8'))
    def change_figure(self,img,**kwargs):
        self.img=img
        self.update_figure(**kwargs)
    def update_figure(self,**kwargs):
        self.draw_figure(**kwargs)
        self.print_figure()
    def draw_figure(self,**kwargs):
        #重新复制
        if self.img.dtype=='uint16':
            self.img_show=np.array(np.floor(self.img/(2**8)),dtype='uint8')
        else:
            self.img_show=np.array(self.img,dtype='uint8')
        if len(self.img.shape)==2:
            self.img_show=cv.cvtColor(self.img_show,cv.COLOR_GRAY2RGB)
        #默认处理：裁剪和中心线显示
        self.img_show=self.Scissor(self.img_show,[self.back.ScissorUp,self.back.ScissorDown,self.back.ScissorLeft,self.back.ScissorRight])
        HEIGHT,WIDTH=self.img_show.shape[0],self.img_show.shape[1]
        if self.back.FlagCenterLine:
            cv.line(self.img_show,(0,HEIGHT//2),(WIDTH-1,HEIGHT//2),(255,255,255),1)
            cv.line(self.img_show,(WIDTH//2,0),(WIDTH//2,HEIGHT-1),(255,255,255),1)
        #补充每个子类的画图方式
    def print_figure(self):
        self.ImgShow=ImageTk.PhotoImage(Image.fromarray(self.img_show))
        self.configure(image=self.ImgShow)
    def Scissor(self,img,cut):#上下左右
        return img[cut[0]:img.shape[0]-cut[1],cut[2]:img.shape[1]-cut[3]]
    def generate_FilenameSave(self):
        return str(self.father.father.back.FigName)+'.tif'#每个类要重写
class ClassFigurePlus(BaseFrame):
    def __init__(self,father,Figure):#Figure为类名
        self.father=father
        self.back=self.father.back
        super().__init__(self.father,padding=5,relief='sunken')
        self.FramePanel=ttk.Frame(self)
        self.FramePanel.pack()
        self.create_FramePanel()
        self.Figure=Figure(self)
        self.Figure.bind('<Motion>',self.MouseMotion)
        self.Figure.pack()
        #补充绑定内容
        self.ButtonR1.config(command=self.Figure.focus_set)
        for j,i in enumerate(self.LE):
            cache=['Up','Down','Left','Right']
            i.pack(side='left')
            i.entry.bind('<Return>',getattr(self,'CommandBindScissor'+cache[j]))
    def create_FramePanel(self):
        #R1
        self.FrameR1=ttk.Frame(self.FramePanel)
        self.FrameR1.pack()
        self.MouseX=tk.IntVar(self)
        self.MouseY=tk.IntVar(self)
        self.Gray=tk.IntVar(self)
        ttk.Label(self.FrameR1,text='X:').pack(side='left')
        ttk.Label(self.FrameR1,textvariable=self.MouseX,width=4).pack(side='left')
        ttk.Label(self.FrameR1,text='Y:').pack(side='left')
        ttk.Label(self.FrameR1,textvariable=self.MouseY,width=4).pack(side='left')
        ttk.Label(self.FrameR1,text='灰度值:').pack(side='left')
        ttk.Label(self.FrameR1,textvariable=self.Gray,width=10).pack(side='left')
        self.ButtonR1=ttk.Button(self.FrameR1,text='focus_set（使用小键盘快捷键请先点击此处）')
        self.ButtonR1.pack(side='left')
        #R2
        self.FrameR2=ttk.Frame(self.FramePanel)
        self.FrameR2.pack()
        self.create_var('ScissorUp',self.back,type='Int',init_value=0,FlagSave=True)
        self.create_var('ScissorDown',self.back,type='Int',init_value=0,FlagSave=True)
        self.create_var('ScissorLeft',self.back,type='Int',init_value=0,FlagSave=True)
        self.create_var('ScissorRight',self.back,type='Int',init_value=0,FlagSave=True)
        self.LE=[LabelEntry(self.FrameR2,text='上裁剪',var=self.ScissorUp),
                 LabelEntry(self.FrameR2,text='下裁剪',var=self.ScissorDown),
                 LabelEntry(self.FrameR2,text='左裁剪',var=self.ScissorLeft),
                 LabelEntry(self.FrameR2,text='右裁剪',var=self.ScissorRight)]
        self.create_var('FlagCenterLine',self.back,type='Boolean',init_value=False,FlagSave=True)
        ttk.Button(self.FrameR2,text='显示/关闭中心线',
                   command=self.CommandButtonCenterLine).pack(side='left')
        #R3
        self.FrameR3=ttk.Frame(self.FramePanel)
        self.FrameR3.pack()
        self.create_var('DirSave',self.back,init_value='',FlagSave=True)
        LabelLabel(self.FrameR3,'保存路径：',self.DirSave,width=50).pack(side='left')
        ttk.Button(self.FrameR3,text='选择文件夹',command=self.CommandButtonR3).pack(side='left')
        #R4
        self.FrameR4=ttk.Frame(self.FramePanel)
        self.FrameR4.pack()
        self.create_var('FilenameSave',self.back,init_value='',FlagSave=True)
        self.LER4=LabelEntry(self.FrameR4,'文件名：',self.FilenameSave,width=50)
        self.LER4.pack(side='left')
        self.LER4.entry.bind('<Return>',self.CommandBindFilenameSave)
        ttk.Button(self.FrameR4,text='生成文件名',command=self.CommandButtonR4_1).pack(side='left')
        ttk.Button(self.FrameR4,text='保存',command=self.CommandButtonR4_2).pack(side='left')
        self.create_var('FlagSaveimg',self.back,type='Boolean',init_value=False)
        ttk.Checkbutton(self.FrameR4,text='保存原图而不是处理后图片',onvalue=True,offvalue=False,
                        variable=self.FlagSaveimg,command=self.CommandCheckButtonSaveimg).pack(side='left')

    
    def MouseMotion(self,event):
        if event.x<self.Figure.img.shape[1]:
            self.MouseX.set(event.x)
        if event.y<self.Figure.img.shape[0]:
            self.MouseY.set(event.y)
        self.Gray.set(self.Figure.img[self.MouseY.get(),self.MouseX.get()])
    def CommandBindScissorUp(self,event):
        self.back.update('ScissorUp',getattr(self,'ScissorUp').get())
        self.Figure.update_figure()
    def CommandBindScissorDown(self,event):
        self.back.update('ScissorDown',getattr(self,'ScissorDown').get())
        self.Figure.update_figure()
    def CommandBindScissorLeft(self,event):
        self.back.update('ScissorLeft',getattr(self,'ScissorLeft').get())
        self.Figure.update_figure()
    def CommandBindScissorRight(self,event):
        self.back.update('ScissorRight',getattr(self,'ScissorRight').get())
        self.Figure.update_figure()
    def CommandButtonCenterLine(self):
        self.back.update('FlagCenterLine',not self.FlagCenterLine.get())
        self.Figure.update_figure()
    
    def CommandButtonR3(self):
        self.back.update('DirSave',filedialog.askdirectory(title='选择文件夹'))

    def CommandButtonR4_1(self):
        self.back.update('FilenameSave',self.Figure.generate_FilenameSave())
    def CommandButtonR4_2(self):
        if self.FlagSaveimg.get():
            savefile=self.Figure.img
        else:
            savefile=cv.cvtColor(self.Figure.img_show,cv.COLOR_RGB2BGR)
        cv.imencode('.tif', savefile)[1].tofile(self.DirSave.get()+'/'+self.FilenameSave.get())
    def CommandBindFilenameSave(self,event):
        self.back.update('FilenameSave',self.FilenameSave.get(),False)
    def CommandCheckButtonSaveimg(self):
        self.back.update('FlagSaveimg',self.FlagSaveimg.get(),False)

    def get_img(self):
        return self.Figure.Scissor(self.Figure.img,[self.back.ScissorUp,self.back.ScissorDown,self.back.ScissorLeft,self.back.ScissorRight])
    def get_img_show(self):
        return self.Figure.img_show
if __name__=='__main__':
    root=tk.Tk()
    ClassFigure(root).pack()
    root.mainloop()