from lib.BaseClass import *
import numpy as np
class DB_MeasureSheet(BaseSubDB):
    def __init__(self,root):
        super().__init__(root)
        self.SubClassName=[]
        #后端变量
        self.TableHeadings=['图名称','帧数','左线','右线','上线','下线','宽度/pix','宽度/mm','长度/pix','长度/mm']
    def update_Sheet_Mouse(self,event):
        if self.ClickMode in ['Up','Down']:
            self.update('Line'+self.ClickMode+'Position',event.y)
        else:
            self.update('Line'+self.ClickMode+'Position',event.x)
        self.update_SheetData()
    def update_Sheet_Key(self,name,delta):
        current=getattr(self,'Line'+self.ClickMode+'Position')+delta
        if name in ['Up','Down'] and self.ClickMode in ['Up','Down']:
            if 0<=current and current<self.Figure.Figure.img.shape[0]:
                self.update('Line'+self.ClickMode+'Position',current)
        elif name in ['Left','Right'] and self.ClickMode in ['Left','Right']:
            if 0<=current and current<self.Figure.Figure.img.shape[1]:
                self.update('Line'+self.ClickMode+'Position',current)
        self.update_SheetData()
    def update_SheetData(self):
        self.update('SheetWidthPix',self.LineRightPosition-self.LineLeftPosition)
        self.update('SheetWidth',self.SheetWidthPix*self.root.Main.FrameChoosePic.PixSize/1000)
        self.update('SheetLengthPix',self.LineDownPosition-self.LineUpPosition)
        self.update('SheetLength',self.SheetLengthPix*self.root.Main.FrameChoosePic.PixSize/1000)
    def generate_data(self):
        return [self.LineLeftPosition,self.LineRightPosition,self.LineUpPosition,self.LineDownPosition,
                self.SheetWidthPix,self.SheetWidth,self.SheetLengthPix,self.SheetLength]
    def generate_title(self):
        cache=np.array(self.root.Main.FrameChoosePic.data)
        c=self.root.Main.FrameChoosePic#
        return ['X',c.ImpactX,'Y',c.ImpactY,'像素大小/um/pix',c.PixSize,'平均液膜宽度/mm',np.mean(cache[:,7]),'平均液膜长度/mm',np.mean(cache[:,9])]
    def get_dir_res(self,classname):
        name=''
        if self.root.Main.FlagDirectFolder:
            name=''
        else:
            name='实验编号'+str(self.root.Main.ExpNo)+'_'
        DirData=self.root.Main.DirData
        return DirData[:DirData.rfind("/")+1]+'液膜信息/'+name+classname+'.xlsx'