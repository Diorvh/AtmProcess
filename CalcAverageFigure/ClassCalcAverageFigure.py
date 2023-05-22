import tkinter as tk
from tkinter import ttk
import cv2 as cv
from lib.lib_tkwidget import *
from lib.ClassFigure import *
from lib.BaseClass import *
from lib.Table import *
from CalcAverageFigure.CalcAverageFigure import *
import time
class ClassFigureCalcAverageFigure(ClassFigure):#改名
    def __init__(self,father):
        super().__init__(father)
    def draw_figure(self, **kwargs):
        super().draw_figure(**kwargs)
    def generate_FilenameSave(self):#每个类要重写
        return str(self.father.father.back.root.Main.generate_ImageLabel)+'_'+str(self.father.father.back.FigStart)+'-'+str(self.father.father.back.FigEnd)+'AverageFigure.tif'
class ClassCalcAverageFigure(BaseFrame):#改名
    def __init__(self,father):
        self.father=father
        self.db=father.db
        self.back=self.father.back.CalcAverageFigure#改名
        super().__init__(self.father,padding=5,relief='sunken')
        self.FramePanel=ttk.Frame(self)
        self.FramePanel.grid(row=0,column=0)
        self.create_panel()
        self.Figure=ClassFigurePlus(self,ClassFigureCalcAverageFigure)#改名
        self.back.Figure=self.Figure
        self.Figure.grid(row=1,column=0)
        #以上为默认，不要动，以下可添加图片绑定功能self.Figure.Figure.bind('<Key>',self.CommandBindFigureKey)
    def create_panel(self):
        #R1
        self.FrameR1=ttk.Frame(self.FramePanel)
        self.FrameR1.pack(side='left')
        self.create_var('FigStart',self.back,'Int',0,True)
        self.create_var('FigEnd',self.back,'Int',0,True)
        self.LER1_1=LabelEntry(self.FrameR1,'起始帧：',self.FigStart)
        self.LER1_1.pack(side='left')
        self.LER1_1.entry.bind('<Return>',self.CommandBindFigStart)
        self.LER1_2=LabelEntry(self.FrameR1,'结束帧：',self.FigEnd)
        self.LER1_2.pack(side='left')
        self.LER1_2.entry.bind('<Return>',self.CommandBindFigEnd)
        ttk.Button(self.FramePanel,text='计算平均图',command=self.CommandButtonCalcAverage).pack(side='left')
    def CommandBindFigStart(self,event):
        self.back.update('FigStart',self.FigStart.get(),False)
    def CommandBindFigEnd(self,event):
        self.back.update('FigEnd',self.FigEnd.get(),False)
    def CommandButtonCalcAverage(self):
        start_time=time.time()
        # img_list=[]
        # for i in range(self.FigStart.get(),self.FigEnd.get()+1):
            # img_list.append(cv.imdecode(np.fromfile(file=self.back.root.Main.generate_fdir()+'/'+str(i)+'.tif',dtype=np.uint8),-1))
        self.FreshSelf(calculate_average_image(self.back.root.Main.generate_fdir(),self.FigStart.get(),self.FigEnd.get(),4))
        print('计算完成，耗时',time.time()-start_time,'秒')

    def FreshSelf(self,img=np.random.randint(0,256,size=(640,704),dtype='uint8')):
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