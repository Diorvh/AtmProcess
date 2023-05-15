from lib.BaseClass import *
import numpy as np
class DB_MeasureSheet(BaseSubDB):
    def __init__(self,root):
        super().__init__(root)
        self.SubClassName=[]
        #后端变量
    def update_Sheet(self,event):
        if self.ClickMode in ['Up','Down']:
            self.update('Line'+self.ClickMode+'Position',event.y)
        else:
            self.update('Line'+self.ClickMode+'Position',event.x)
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
        return ['平均液膜宽度/mm',np.mean(cache[:,7]),'平均液膜长度/mm',np.mean(cache[:,9])]