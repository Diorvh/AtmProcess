import tkinter as tk
from tkinter import ttk
import cv2 as cv
from lib.lib_tkwidget import *
from lib.ClassFigure import *
from lib.BaseClass import *
from lib.Table import *
class ClassFigureMeasureBreakupLength(ClassFigure):
    def __init__(self,father):
        super().__init__(father)
    def draw_figure(self, **kwargs):
        super().draw_figure(**kwargs)
        cv.line(self.img_show,
                (0,self.back.get('BreakupPosition')),
                (self.img.shape[1],self.back.get('BreakupPosition')),
                (255,0,0),1)
    def generate_FilenameSave(self):#每个类要重写
        return str(self.father.father.back.FigName)+'.tif'
class ClassMeasureBreakupLength(BaseFrame):
    def __init__(self,father):
        self.father=father
        self.db=father.db
        self.back=self.db.Main.FrameChoosePic.MeasureBreakupLength
        super().__init__(self.father,padding=5,relief='sunken')
        self.FramePanel=ttk.Frame(self)
        self.FramePanel.grid(row=0,column=0)
        self.create_panel()
        self.Figure=ClassFigurePlus(self,ClassFigureMeasureBreakupLength)
        self.back.Figure=self.Figure
        self.Figure.grid(row=1,column=0)
        self.Figure.Figure.bind('<Key>',self.CommandBindFigureKey)
        self.Figure.Figure.bind('<Button-1>',self.CommandBindFigureButton1)
    def create_panel(self):
        #R1
        self.create_var('BreakupPosition',self.back,type='Int',init_value=0,FlagSave=True)
        self.create_var('BreakupLengthPix',self.back,type='Int',init_value=0,FlagSave=True)
        self.create_var('BreakupLength',self.back,type='Double',init_value=0,FlagSave=True)
        LabelLabel(self.FramePanel,'破碎线:',self.BreakupPosition,width=5).grid(row=0,column=0,sticky='W')
        LabelLabel(self.FramePanel,'破碎长度:',self.BreakupLengthPix,width=5,extratext='pix').grid(row=0,column=1,sticky='W')
        LabelLabel(self.FramePanel,'破碎长度:',self.BreakupLength,width=5,extratext='mm').grid(row=0,column=2,sticky='W')
        self.create_var('FileResultsIn',self.back,init_value='',FlagSave=True)
        ChooseFile(self.FramePanel,'结果读入目录:',self.FileResultsIn).grid(row=1,column=0,columnspan=3)
        # ttk.Button(self.FramePanel,text='读入结果',command=CommandButtonRead).grid(row=1,column=3)
    def CommandBindFigureKey(self,event):
        if event.char=='3':#保存过
            self.father.CommandButtonFigNameInc()
        elif event.char=='9':#不保存退
            self.father.CommandButtonFigNameDec()
        elif event.char=='5':#不保存过
            self.father.FigNameChangeOnly(1)
        elif event.keysym=='Up':
            self.back.update_Sheet_Key(-1)
            self.FreshSelf()
        elif event.keysym=='Down':
            self.back.update_Sheet_Key(1)
            self.FreshSelf()
    def CommandBindFigureButton1(self,event):
        self.back.update_Sheet_Mouse(event)
        self.FreshSelf()
    def FreshSelf(self):
        self.back.update_SheetData()
        img=cv.imdecode(np.fromfile(file=self.back.root.Main.FrameChoosePic.get_dir_tif(),dtype=np.uint8),-1)
        self.Figure.Figure.change_figure(img)