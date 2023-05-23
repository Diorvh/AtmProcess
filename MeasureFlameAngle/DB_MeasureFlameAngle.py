from lib.BaseClass import *
import numpy as np
from MeasureFlameAngle.CalcFlameAngle import *
class DB_MeasureFlameAngle(BaseSubDB):
    def __init__(self,root):
        super().__init__(root)
        self.SubClassName=[]
        #后端变量
        self.TableHeadings=['图名称','帧数','宽度/pix','宽度/mm','长度/pix','长度/mm']
    def generate_data(self):
        return [1]
    def generate_title(self):
        return ['上裁剪','下裁剪','左裁剪','右裁剪']
    def Fresh(self):
        img=self.Figure.get_img()
        father=self.root.Main.FrameChoosePic
        res=calc_theta(img,father.ImpactX,father.ImpactY,self.Threshold)
        self.update('AngleM',res[0])
        self.update('AngleL',res[1])
        self.update('AngleR',res[2])
        self.update('Angle',self.AngleR-self.AngleL)
        res=calc_y(img,self.Threshold)
        self.update('YCenter',res[0])
        self.update('YStart',res[1])
        self.update('YEnd',res[2])
        self.update('YLength',self.YEnd-self.YStart)