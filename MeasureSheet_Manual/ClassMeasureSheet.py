import tkinter as tk
from tkinter import ttk
import cv2 as cv
from lib.lib_tkwidget import *
from lib.ClassFigure import *
from lib.BaseClass import *
from lib.Table import *
class ClassFigureMeasureSheet(ClassFigure):
    def __init__(self,father):
        super().__init__(father)
    def draw_figure(self, **kwargs):
        super().draw_figure(**kwargs)
        cv.line(self.img_show,
                (self.back.get('LineLeftPosition'),0),
                (self.back.get('LineLeftPosition'),self.img.shape[0]),
                (255,0,0),1)
        cv.line(self.img_show,
                (self.back.get('LineRightPosition'),0),
                (self.back.get('LineRightPosition'),self.img.shape[0]),
                (255,0,0),1)
        cv.line(self.img_show,
                (0,self.back.get('LineUpPosition')),
                (self.img.shape[1],self.back.get('LineUpPosition')),
                (255,0,0),1)
        cv.line(self.img_show,
                (0,self.back.get('LineDownPosition')),
                (self.img.shape[1],self.back.get('LineDownPosition')),
                (255,0,0),1)
class ClassMeasureSheet(BaseFrame):
    def __init__(self,father):
        self.father=father
        self.db=father.db
        self.back=self.db.Main.FrameChoosePic.MeasureSheet
        super().__init__(self.father,padding=5,relief='sunken')
        self.FramePanel=ttk.Frame(self)
        self.FramePanel.grid(row=0,column=0)
        self.create_panel()
        # self.Figure.LabelFigure.bind('<Key>',self.CommandBindKey)
        # self.Figure.LabelFigure.bind('<Button-1>',self.CommandBindKey)
        self.Figure=ClassFigurePlus(self,ClassFigureMeasureSheet)
        self.back.Figure=self.Figure
        self.Figure.grid(row=1,column=0)
        self.Figure.Figure.bind('<Key>',self.CommandBindFigureKey)
        self.Figure.Figure.bind('<Button-1>',self.CommandBindFigureButton1)
    def create_panel(self):
        #R1
        self.create_var('LineLeftPosition',self.back,type='Int',init_value=0,FlagSave=True)
        self.create_var('LineRightPosition',self.back,type='Int',init_value=0,FlagSave=True)
        self.create_var('SheetWidthPix',self.back,type='Int',init_value=0,FlagSave=True)
        self.create_var('SheetWidth',self.back,type='Double',init_value=0,FlagSave=True)
        LabelLabel(self.FramePanel,'左线:',self.LineLeftPosition,width=5).grid(row=0,column=0,sticky='W')
        LabelLabel(self.FramePanel,'右线:',self.LineRightPosition,width=5).grid(row=0,column=1,sticky='W')
        LabelLabel(self.FramePanel,'液膜宽度:',self.SheetWidthPix,width=5,extratext='pix').grid(row=0,column=2,sticky='W')
        LabelLabel(self.FramePanel,'液膜宽度:',self.SheetWidth,width=5,extratext='mm').grid(row=0,column=3,sticky='W')
        #R2
        self.create_var('LineUpPosition',self.back,type='Int',init_value=0,FlagSave=True)
        self.create_var('LineDownPosition',self.back,type='Int',init_value=0,FlagSave=True)
        self.create_var('SheetLengthPix',self.back,type='Int',init_value=0,FlagSave=True)
        self.create_var('SheetLength',self.back,type='Double',init_value=0,FlagSave=True)
        LabelLabel(self.FramePanel,'上线:',self.LineUpPosition,width=5).grid(row=1,column=0,sticky='W')
        LabelLabel(self.FramePanel,'下线:',self.LineDownPosition,width=5).grid(row=1,column=1,sticky='W')
        LabelLabel(self.FramePanel,'液膜长度:',self.SheetLengthPix,width=5,extratext='pix').grid(row=1,column=2,sticky='W')
        LabelLabel(self.FramePanel,'液膜长度:',self.SheetLength,width=5,extratext='mm').grid(row=1,column=3,sticky='W')
        #R3
        ttk.Button(self.FramePanel,text='移动左线',command=lambda:self.CommandButtonLine('Left')).grid(row=2,column=0,sticky='NSWE')
        ttk.Button(self.FramePanel,text='移动右线',command=lambda:self.CommandButtonLine('Right')).grid(row=2,column=1,sticky='NSWE')
        #R4
        ttk.Button(self.FramePanel,text='移动上线',command=lambda:self.CommandButtonLine('Up')).grid(row=3,column=0,sticky='NSWE')
        ttk.Button(self.FramePanel,text='移动下线',command=lambda:self.CommandButtonLine('Down')).grid(row=3,column=1,sticky='NSWE')
        self.create_var('ClickMode',self.back,type='String',init_value='Left',FlagSave=True)
        LabelLabel(self.FramePanel,text='当前移动线：',var=self.ClickMode).grid(row=2,rowspan=2,column=2,columnspan=2,sticky='NSWE')
    def CommandButtonLine(self,value):
        self.back.update('ClickMode',value)
    def CommandBindFigureKey(self,event):
        dict={'2':'Down','4':'Left','6':'Right','8':'Up'}
        if event.char in dict:
            self.back.update('ClickMode',dict[event.char])
        elif event.char=='3':
            self.father.CommandButtonFigNameInc()
        elif event.char=='9':
            self.father.CommandButtonFigNameDec()
        elif event.keysym in ['Up','Left']:
            self.back.update_Sheet_Key(event.keysym,-1)
            self.FreshSelf()
        elif event.keysym in ['Down','Right']:
            self.back.update_Sheet_Key(event.keysym,1)
            self.FreshSelf()
    def CommandBindFigureButton1(self,event):
        self.back.update_Sheet_Mouse(event)
        self.FreshSelf()
    def FreshSelf(self):
        self.back.update_SheetData()
        img=cv.imdecode(np.fromfile(file=self.back.root.Main.FrameChoosePic.get_dir_tif(),dtype=np.uint8),-1)
        self.Figure.Figure.change_figure(img)
    # def update_figure(self):
    #     self.Figure.update_figure(self.master.master.DirData.get()+r'/原位/'+self.master.CurrentName.get()+'.tif',
    #                                   Point=(self.master.ImpactX.get(),self.master.ImpactY.get()),
    #                                   Point1=(self.LineLeftx,self.LineLefty),
    #                                   Point2=(self.LineRightx,self.LineRighty))
    # def get_res(self):
    #     return [self.Angle.get(),
    #             self.master.ImpactX.get(),self.master.ImpactY.get(),
    #             self.LineLeftx,self.LineLefty,
    #             self.LineRightx,self.LineRighty]
    # def CommandBindKey(self,event):
    #     if event.char=='4':
    #         self.click_mode='left'#TODO:改变button为关闭
    #     elif event.char=='6':
    #         self.click_mode='right'
    # def CommandBindButton1(self,event):
    #     try:
    #         c,d=self.Figure.img[:,event.x],self.Figure.img[event.y,:]#检测是否超出范围外
    #         if self.click_mode=='left':
    #             self.LineLefty,self.LineLeftx=event.x+1,event.y+1#和pcc读取坐标一致
    #         else:
    #             self.LineRighty,self.LineRightx=event.x+1,event.y+1#和pcc读取坐标一致
    #         self.Angle.set(calc_angle(self.master.ImpactX.get(),self.master.ImpactY.get(),
    #                               self.LineLeftx,self.LineLefty,
    #                               self.LineRightx,self.LineRighty))
    #         self.update_figure()
    #     except:
#     #         pass
# def calc_angle(ix,iy,lx,ly,rx,ry):
#     return (np.arctan((ix-lx)/(ly-iy))+np.arctan((rx-ix)/(ry-iy)))/np.pi*180
# class ClassFigureMeasureSheet(ClassFigure):
#     def __init__(self,master):
#         super().__init__(master)
#     def draw_figure(self,**kwargs):
#         super().draw_figure()
#         x0,y0=kwargs['Point']
#         x1,y1=kwargs['Point1']
#         x1,y1=x1+(x1-x0)*1000,y1+(y1-y0)*1000
#         x2,y2=kwargs['Point2']
#         x2,y2=x2+(x2-x0)*1000,y2+(y2-y0)*1000
#         cv.line(self.img_show,(x0,y0),(x1,y1),(255,0,0),1)
#         cv.line(self.img_show,(x0,y0),(x2,y2),(255,0,0),1)
if __name__=='__main__':
    root=tk.Tk()
    App=ClassMeasureSheet(root)
    App.pack()
    # root.protocol("WM_DELETE_WINDOW",close_window)
    root.mainloop()