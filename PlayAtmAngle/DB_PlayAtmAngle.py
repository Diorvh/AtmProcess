from lib.BaseClass import *
import numpy as np
from lib.lib_Angle import *
class DB_PlayAtmAngle(BaseSubDB):#改名
    def __init__(self,root):
        super().__init__(root)
        self.SubClassName=[]
        #后端变量
        self.TableHeadings=[]
    def generate_data(self):
        return []
    def generate_title(self):#TODO:和前端计算出的数据结合
        cache=np.array(self.root.Main.FrameChoosePic.data)
        back=self.root.Main.FrameChoosePic
        return ['左点X',self.XLeft,'右点X',self.XRight,'Y',self.Y,'Thres',self.Thres,
                '雾化锥角/°',self.Angle,'雾化锥角标准差/°','雾化锥角相对标准差/°']
    def Fresh(self):#TODO:没有调整
        img=self.Figure.get_img()
        father=self.root.Main.FrameChoosePic
        self.resL,self.resR=calculate_atmangle(65535-img,self.XLeft,self.XRight,father.ImpactX,self.Y,self.Thres)
        # self.update('AngleM',res[0])
        # self.update('AngleL',res[1])
        # self.update('AngleR',res[2])
        # self.update('Angle',self.AngleR-self.AngleL)