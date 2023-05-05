import tkinter as tk
from tkinter import ttk
from lib_tkwidget import *
from ClassFigure import *
class ClassFigureMeasureSheet(ClassFigure):
    def __init__(self,master):
        super().__init__(master)
    def draw_figure(self, **kwargs):
        pass
class ClassMeasureSheet(ttk.Frame):
    def __init__(self,master):
        self.father=master
        self.db=master.db
        super().__init__(self.father,padding=5,relief='sunken')
        # self.click_mode='left'
        # self.LineLefty,self.LineLeftx,self.LineRighty,self.LineRightx=0,0,0,0
        self.create_panel()
        # self.Figure.LabelFigure.bind('<Key>',self.CommandBindKey)
        # self.Figure.LabelFigure.bind('<Button-1>',self.CommandBindKey)
        self.Figure=ClassFigureMeasureSheet(self)
        self.Figure.pack()
    def create_panel(self):
        self.FramePanel=ttk.Frame(self)
        self.FramePanel.pack()
        #R1
        self.LineLeftPosition=tk.IntVar(self)
        self.LineRightPosition=tk.IntVar(self)
        self.SheetWidthPix=tk.IntVar(self)
        self.SheetWidth=tk.DoubleVar(self)
        LabelLabel(self.FramePanel,'左线:',self.LineLeftPosition,width=5).grid(row=0,column=0,sticky='W')
        LabelLabel(self.FramePanel,'右线:',self.LineLeftPosition,width=5).grid(row=0,column=1,sticky='W')
        LabelLabel(self.FramePanel,'液膜宽度:',self.LineLeftPosition,width=5,extratext='pix').grid(row=0,column=2,sticky='W')
        LabelLabel(self.FramePanel,'液膜宽度:',self.LineLeftPosition,width=5,extratext='mm').grid(row=0,column=3,sticky='W')
        #R2
        self.LineUpPosition=tk.IntVar(self)
        self.LineDownPosition=tk.IntVar(self)
        self.SheetLengthPix=tk.IntVar(self)
        self.SheetLength=tk.DoubleVar(self)
        LabelLabel(self.FramePanel,'上线:',self.LineLeftPosition,width=5).grid(row=1,column=0,sticky='W')
        LabelLabel(self.FramePanel,'下线:',self.LineLeftPosition,width=5).grid(row=1,column=1,sticky='W')
        LabelLabel(self.FramePanel,'液膜长度:',self.LineLeftPosition,width=5,extratext='pix').grid(row=1,column=2,sticky='W')
        LabelLabel(self.FramePanel,'液膜长度:',self.LineLeftPosition,width=5,extratext='mm').grid(row=1,column=3,sticky='W')
        #R3
        self.ButtonLeft=ttk.Button(self.FramePanel,text='移动左线',command=self.CommandButtonLeftLine).grid(row=2,column=0,sticky='NSWE')
        self.ButtonRight=ttk.Button(self.FramePanel,text='移动右线',command=self.CommandButtonRightLine).grid(row=2,column=1,sticky='NSWE')
        #R4
        self.ButtonLeft=ttk.Button(self.FramePanel,text='移动上线',command=self.CommandButtonUpLine).grid(row=3,column=0,sticky='NSWE')
        self.ButtonRight=ttk.Button(self.FramePanel,text='移动下线',command=self.CommandButtonDownLine).grid(row=3,column=1,sticky='NSWE')
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
    def CommandButtonLeftLine(self):
        self.click_mode='left'
    def CommandButtonRightLine(self):
        self.click_mode='right'
    def CommandButtonUpLine(self):
        self.click_mode='Up'
    def CommandButtonDownLine(self):
        self.click_mode='Down'
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