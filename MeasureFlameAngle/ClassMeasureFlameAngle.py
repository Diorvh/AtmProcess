import tkinter as tk
from tkinter import ttk
import cv2 as cv
from lib.lib_tkwidget import *
from lib.ClassFigure import *
from lib.BaseClass import *
from lib.Table import *
class ClassFigureMeasureFlameAngle(ClassFigure):
    def __init__(self,father):
        super().__init__(father)
    def draw_figure(self, **kwargs):
        super().draw_figure(**kwargs)
class ClassMeasureFlameAngle(BaseFrame):
    def __init__(self,father):
        self.father=father
        self.db=father.db
        self.back=self.father.back.MeasureFlameAngle
        super().__init__(self.father,padding=5,relief='sunken')
        self.FramePanel=ttk.Frame(self)
        self.FramePanel.grid(row=0,column=0)
        self.create_panel()
        self.Figure=ClassFigurePlus(self,ClassFigureMeasureFlameAngle)
        self.back.Figure=self.Figure
        self.Figure.grid(row=1,column=0)
        # self.Figure.Figure.bind('<Key>',self.CommandBindFigureKey)
        # self.Figure.Figure.bind('<Button-1>',self.CommandBindFigureButton1)
    def create_panel(self):
        #R1
        ttk.Label(self.FramePanel,text='adsfjsalkfdjalkdfjlfdj')
    def FreshSelf(self):
        # self.back.update_SheetData()
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
# if __name__=='__main__':
#     root=tk.Tk()
#     App=ClassMeasureSheet(root)
#     App.pack()
#     # root.protocol("WM_DELETE_WINDOW",close_window)
#     root.mainloop()