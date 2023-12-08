from lib.BaseClass import *
import numpy as np
from lib.lib_Angle import *
class DB_MeasureFlameAngle(BaseSubDB):
    def __init__(self,root):
        super().__init__(root)
        self.SubClassName=[]
        #后端变量
        self.TableHeadings=[]
    def generate_data(self):
        return [1]
    def generate_title(self):
        back=self.root.Main.FrameChoosePic
        return ['左裁剪/pix',self.ScissorLeft,'右裁剪/pix',self.ScissorLeft,'撞击点X',back.ImpactX,'撞击点Y',back.ImpactY,
                'thres',self.Threshold,'AngleL',self.AngleL,'AngleR',self.AngleR,'AngleM',self.AngleM,'Angle',self.Angle,
                'YStart',self.YStart,'YEnd',self.YEnd,'YCenter',self.YCenter,'YLength',self.YLength]
    def Fresh(self):
        img=self.Figure.get_img()
        father=self.root.Main.FrameChoosePic
        res=calc_theta(img,father.ImpactX,father.ImpactY,self.Threshold)
        self.update('AngleM',res[0])
        self.update('AngleL',res[1])
        self.update('AngleR',res[2])
        self.update('Angle',self.AngleR-self.AngleL)
        # res=calc_y(img,self.Threshold)#旧的提取y方向参数
        # res=calc_Rparameter(img,father.ImpactX,father.ImpactY,self.Threshold,np.round(self.AngleL,1),np.round(self.AngleR,1))#根据灰度值和提取参数
        res=calc_Rparameter_flamedirection(img,father.ImpactX,father.ImpactY,self.Threshold,np.round(self.AngleM,1))
        # self.update('YCenter',res[0])#新版文章取消了这个概念
        self.update('YStart',res[0])
        self.update('YEnd',res[1])
        self.update('YLength',self.YEnd-self.YStart)