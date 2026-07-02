from lib.BaseClass import *
import numpy as np
from services.breakup_length_service import BreakupLengthService
class DB_MeasureBreakupLength(BaseSubDB):
    def __init__(self,root):
        super().__init__(root)
        self.SubClassName=[]
        self.service=BreakupLengthService()
        #后端变量
        self.TableHeadings=['图名称','帧数','破碎线','破碎长度/pix','破碎长度/mm']
    def update_Sheet_Mouse(self,event):
        self.update('BreakupPosition',event.y)
        self.update_SheetData()
    def update_Sheet_Key(self,delta):
        current=self.BreakupPosition+delta
        if 0<=current and current<self.Figure.Figure.img.shape[0]:
            self.update('BreakupPosition',current)
        self.update_SheetData()
    def update_SheetData(self):
        result=self.service.calculate(self.BreakupPosition,self.root.Main.FrameChoosePic.ImpactY,self.root.Main.FrameChoosePic.PixSize)
        self.update('BreakupLengthPix',result.length_px)
        self.update('BreakupLength',result.length_mm)
    def generate_data(self):
        return [self.BreakupPosition,self.BreakupLengthPix,self.BreakupLength]
    def generate_title(self):
        cache=np.array(self.root.Main.FrameChoosePic.data)
        c=self.root.Main.FrameChoosePic
        t,lb=cache[:,1],cache[:,4]
        sum=0
        for j in range(len(t)-1):
            sum+=(t[j+1]-t[j]+1)*(lb[j+1]+lb[j])/2
        sum=sum-np.sum(lb)+lb[0]+lb[-1]
        ans=sum/(t[-1]-t[0]+1)
        return ['X',c.ImpactX,'Y',c.ImpactY,'像素大小/um/pix',c.PixSize,'平均破碎长度/mm',ans,'半数采样破碎长度/mm',np.average(lb[::2]),
                'Decimate',c.Decimate,'总张数',len(t),'起始帧',t[0],'结束帧',t[-1]]
    def get_dir_res(self,classname):
        name=''
        if self.root.Main.FlagDirectFolder:
            name=''
        else:
            name='实验编号'+str(self.root.Main.ExpNo)+'_'
        DirData=self.root.Main.DirData
        return DirData[:DirData.rfind("/")+1]+'破碎长度/'+name+classname+'.xlsx'
