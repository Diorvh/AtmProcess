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
        self.create_var('Gain',self.back,'Double',1,True)
        self.create_var('Threshold',self.back,'Double',0.1,True)
        self.LER1_1=LabelEntry(self.FramePanel,'增益=',self.Gain)
        self.LER1_1.grid(row=0,column=0,columnspan=2,sticky='w')
        self.LER1_1.entry.bind('<Return>',self.CommandBindGain)
        self.LER1_2=LabelEntry(self.FramePanel,'单侧阈值=',self.Threshold)
        self.LER1_2.grid(row=0,column=2,columnspan=2,sticky='w')
        self.LER1_2.entry.bind('<Return>',self.CommandBindThreshold)
        self.create_var('FlagPColor',self.back,'Boolean',False,True)
        self.ButtonR1=ttk.Button(self.FramePanel,text='显示伪彩图',command=self.CommandButtonR1)
        self.ButtonR1.grid(row=0,column=4,sticky='we')
        #R2
        self.create_var('AngleO',self.back,'Double',0,True)
        self.create_var('AngleF',self.back,'Double',0,True)
        self.create_var('AngleCalc',self.back,'Double',0,True)
        self.LER2_1=LabelEntry(self.FramePanel,'氧化剂夹角=',self.AngleO)
        self.LER2_1.grid(row=1,column=0,sticky='w')
        self.LER2_1.entry.bind('<Return>',self.CommandBindAngleO)
        self.LER2_2=LabelEntry(self.FramePanel,'燃料夹角=',self.AngleF)
        self.LER2_2.grid(row=1,column=1,sticky='w')
        self.LER2_2.entry.bind('<Return>',self.CommandBindAngleF)
        self.LER2_3=LabelEntry(self.FramePanel,'合成动量夹角(O+)=',self.AngleCalc)
        self.LER2_3.grid(row=1,column=2,columnspan=2,sticky='w')
        self.LER2_3.entry.bind('<Return>',self.CommandBindAngleCalc)
        self.create_var('FlagLineTheo',self.back,'Boolean',False,True)
        self.ButtonR2=ttk.Button(self.FramePanel,text='显示理论线',command=self.CommandButtonR2)
        self.ButtonR2.grid(row=1,column=4,sticky='we')
        #R3
        self.create_var('AngleL',self.back,'Double',0,True)
        self.create_var('AngleR',self.back,'Double',0,True)
        self.create_var('AngleM',self.back,'Double',0,True)
        self.create_var('Angle',self.back,'Double',0,True)
        LabelLabel(self.FramePanel,'左边界角=',self.AngleL,extratext='°').grid(row=2,column=0,sticky='w')
        LabelLabel(self.FramePanel,'右边界角=',self.AngleR,extratext='°').grid(row=2,column=1,sticky='w')
        LabelLabel(self.FramePanel,'中心线角=',self.AngleM,extratext='°').grid(row=2,column=2,sticky='w')
        LabelLabel(self.FramePanel,'火焰锥角=',self.Angle,extratext='°').grid(row=2,column=3,sticky='w')
        self.create_var('FlagLineAngle',self.back,'Boolean',False,True)
        self.ButtonR3=ttk.Button(self.FramePanel,text='显示锥角线',command=self.CommandButtonR3)
        self.ButtonR3.grid(row=2,column=4,sticky='we')
        #R4
        self.create_var('YStart',self.back,'Double',0,True)
        self.create_var('YEnd',self.back,'Double',0,True)
        self.create_var('YCenter',self.back,'Double',0,True)
        self.create_var('YLength',self.back,'Double',0,True)
        LabelLabel(self.FramePanel,'火焰起始=',self.YStart,extratext='pix').grid(row=3,column=0,sticky='w')
        LabelLabel(self.FramePanel,'火焰结束=',self.YEnd,extratext='pix').grid(row=3,column=1,sticky='w')
        LabelLabel(self.FramePanel,'火焰中心=',self.YCenter,extratext='pix').grid(row=3,column=2,sticky='w')
        LabelLabel(self.FramePanel,'火焰长度=',self.YLength,extratext='pix').grid(row=3,column=3,sticky='w')
        self.create_var('FlagLineY',self.back,'Boolean',False,True)
        self.ButtonR4=ttk.Button(self.FramePanel,text='显示火焰长度线',command=self.CommandButtonR4)
        self.ButtonR4.grid(row=3,column=4,sticky='we')

    def CommandBindGain(self,event):
        self.back.update('Gain',self.Gain.get(),False)
        self.FreshSelf()
    def CommandBindThreshold(self,event):
        self.back.update('Threshold',self.Threshold.get(),False)
        self.FreshSelf()
    def CommandButtonR1(self):
        self.back.update('FlagPColor',not self.FlagPColor.get())
        self.ButtonR1.config(text='关闭伪彩图' if self.FlagPColor.get() else '显示伪彩图')
        self.FreshSelf()

    def CommandBindAngleO(self,event):
        self.back.update('AngleO',self.AngleO.get(),False)
        self.FreshSelf()
    def CommandBindAngleF(self,event):
        self.back.update('AngleF',self.AngleF.get(),False)
        self.FreshSelf()
    def CommandBindAngleCalc(self,event):
        self.back.update('AngleCalc',self.AngleCalc.get(),False)
        self.FreshSelf()
    def CommandButtonR2(self):
        self.back.update('FlagLineTheo',not self.FlagLineTheo.get())
        self.ButtonR2.config(text='关闭理论线' if self.FlagLineTheo.get() else '显示理论线')
        self.FreshSelf()

    def CommandButtonR3(self):
        self.back.update('FlagLineAngle',not self.FlagLineAngle.get())
        self.ButtonR3.config(text='关闭锥角线' if self.FlagLineAngle.get() else '显示锥角线')
        self.FreshSelf()

    def CommandButtonR4(self):
        self.back.update('FlagLineY',not self.FlagLineY.get())
        self.ButtonR4.config(text='关闭火焰长度线' if self.FlagLineY.get() else '显示火焰长度线')
        self.FreshSelf()    

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