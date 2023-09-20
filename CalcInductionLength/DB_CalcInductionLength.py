from lib.BaseClass import *
import numpy as np
from CalcInductionLength.CalcInductionLength import *
from lib.dft import *
class DB_CalcInductionLength(BaseSubDB):#改名
    def __init__(self,root):
        super().__init__(root)
        self.SubClassName=[]
        #后端变量
        self.TableHeadings=['距撞击点距离/pix','距撞击点距离/um','灰度值','频谱强度']
        for i in range(10,101):
            self.TableHeadings.append(str(i)+'Hz低通灰度值差分')
        self.gray=[]
    def generate_data(self):#保存数据
        data=np.array(list(range(len(self.gray))))#距撞击点距离/pix
        data=np.c_[data,data*self.root.Main.FrameChoosePic.PixSize]#距撞击点距离/um
        data=np.c_[data,self.gray]#灰度值
        data=np.c_[data,dft(self.gray)[1]]#频谱强度
        data=np.insert(data,0,np.zeros((1,4)),axis=0)
        for i in range(10,101):
            graylowpass=lowpass(self.gray,len(self.gray),i)
            graydiff=calc_graydiff(graylowpass)
            graydiff=np.insert(graydiff,0,np.array(np.argmax(graydiff[50:])+50))
            data=np.c_[data,graydiff]
        return data
    def generate_title(self):#第一行
        return ['角度/°',self.AngleM,'像素尺寸/mm/pix',self.root.Main.FrameChoosePic.PixSize,'数据第一行为差分最大值位置']
