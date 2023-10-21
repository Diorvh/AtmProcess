from lib.BaseClass import *
import numpy as np
from lib.lib_AtmAngle import *
from scipy.signal import savgol_filter
from PlayAtmAngle.PlayAtmAngle import *
import time
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
        start_time=time.time()
        self.resL,self.resR=mul_calculate_grayavg_byangle(65535-img,self.XLeft,self.XRight,self.Y,self.root.Main.CoreNum,self.Rmax,(899,self.ThetaLeft),(901,self.ThetaRight))#需要验证，不进行对称裁剪是否有影响
        print('计算完成，耗时',time.time()-start_time,'秒')
        self.resLSG=[self.resL[0],savgol_filter(self.resL[1],self.window_length,self.polyorder)]
        self.resRSG=[self.resR[0],savgol_filter(self.resR[1],self.window_length,self.polyorder)]
        self.resLSGdiff1=[self.resL[0],savgol_filter(self.resL[1],self.window_length,self.polyorder,deriv=1)]
        self.resRSGdiff1=[self.resR[0],savgol_filter(self.resR[1],self.window_length,self.polyorder,deriv=1)]
        self.resLSGdiff2=[self.resL[0],savgol_filter(self.resL[1],self.window_length,self.polyorder,deriv=2)]
        self.resRSGdiff2=[self.resR[0],savgol_filter(self.resR[1],self.window_length,self.polyorder,deriv=2)]
        EffLPos=np.where((self.ThetaRangeLeft1*0.1<=self.resLSGdiff2[0])&(self.resLSGdiff2[0]<=self.ThetaRangeLeft2*0.1))[0]#提取范围内的下标
        EffRPos=np.where((self.ThetaRangeRight1*0.1<=self.resRSGdiff2[0])&(self.resRSGdiff2[0]<=self.ThetaRangeRight2*0.1))[0]#提取范围内的下标
        AngleL=self.resLSGdiff2[0][EffLPos]#提取范围内的角度
        AngleR=self.resRSGdiff2[0][EffRPos]#提取范围内的角度
        AngleLPos=np.argmin(self.resLSGdiff2[1][EffLPos])#左边界下标
        AngleRPos=np.argmin(self.resRSGdiff2[1][EffRPos])#右边界下标
        self.update('AngleL',AngleL[AngleLPos])
        self.update('AngleR',AngleR[AngleRPos])
        self.update('Angle',self.AngleR-self.AngleL)