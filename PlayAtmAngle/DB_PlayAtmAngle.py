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
        self.resL,self.resR=mul_calculate_grayavg_byangle(65535-img,self.XLeft,self.XRight,self.Y,self.Rmax,(899,self.ThetaLeft),(901,self.ThetaRight),self.NumAvgL,self.RStartL,self.NumAvgR,self.RStartR)#需要验证，不进行对称裁剪是否有影响
        print('计算完成，耗时',time.time()-start_time,'秒')
        #先用原始曲线计算阈值
        cache_max=np.average(self.resL[1][:self.NumAvgL])
        cache_min=np.average(self.resL[1][-self.NumAvgL:])
        ThresL=cache_min+(cache_max-cache_min)*self.ThresRatioL
        cache_max=np.average(self.resR[1][:self.NumAvgR])
        cache_min=np.average(self.resR[1][-self.NumAvgR:])
        ThresR=cache_min+(cache_max-cache_min)*self.ThresRatioR
        #再到滤波后的曲线中去找,找到滤波后曲线最接近阈值的元素的位置
        self.resLSG=[self.resL[0],savgol_filter(self.resL[1],self.window_length,self.polyorder)]
        self.resRSG=[self.resR[0],savgol_filter(self.resR[1],self.window_length,self.polyorder)]
        AngleLPos=np.abs(self.resLSG[1]-ThresL).argmin()
        AngleRPos=np.abs(self.resRSG[1]-ThresR).argmin()
        #更新
        self.update('AngleL',self.resL[0][AngleLPos])
        self.update('AngleR',self.resR[0][AngleRPos])
        self.update('Angle',self.AngleR-self.AngleL)