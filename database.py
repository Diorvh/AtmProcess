from lib.lib_json import *
from lib.BaseClass import *
from MeasureSheet.DB_MeasureSheet import *
from MeasureFlameAngle.DB_MeasureFlameAngle import *
from MeasureBreakupLength.DB_MeasureBreakupLength import *
from CalcAverageFigure.DB_CalcAverageFigure import *
from CalcFlameAngle.DB_CalcFlameAngle import *
import os
import numpy as np
class DB:
    def __init__(self):
        self.SubClassName=['Main']
        self.Main=DB_main(self)
    def load(self):
        try:
            dict=read_json('settings.json')
            for i in self.SubClassName:
                getattr(self,i).load(dict)
        except:
            print('settings.json文件不存在或为空，未读取')
    def save(self):
        dict={}
        for i in self.SubClassName:
            dict={**dict,**getattr(self,i).save()}
        write_json('settings.json',dict)
class DB_main(BaseSubDB):
    def __init__(self,root):
        super().__init__(root)
        self.SubClassName=['FrameChoosePic']
        self.FrameChoosePic=DB_FrameChoosePic(self.root)
    def generate_fdir(self):
        if self.FlagOther:
            return self.DirData+'/'+self.Other
        else:
            return self.DirData+'/实验编号'+str(self.ExpNo)
    def generate_ImageLabel(self):
        if self.FlagDirect:
            return self.ImageLabel
        elif self.FlagOther:
            return self.Other
        else:
            return self.ExpNo
class DB_FrameChoosePic(BaseSubDB):
    def __init__(self,root):
        super().__init__(root)
        self.SubClassName=['MeasureSheet','MeasureBreakupLength','MeasureFlameAngle','CalcAverageFigure','CalcFlameAngle']#增加实例
        self.MeasureSheet=DB_MeasureSheet(self.root)
        self.MeasureBreakupLength=DB_MeasureBreakupLength(self.root)
        self.MeasureFlameAngle=DB_MeasureFlameAngle(self.root)
        self.CalcAverageFigure=DB_CalcAverageFigure(self.root)
        self.CalcFlameAngle=DB_CalcFlameAngle(self.root)#增加实例
        #后端变量
        self.FigureNameList=[]
        self.data=[]
    def Fresh(self):#update_FigureNameList
        if not self.root.Main.FlagDirect:
            filename=os.listdir(self.root.Main.generate_fdir())
            filename=[x for x in filename if x.endswith('.tif')]#只保留tif结尾的
            filename=[int(x[:-4]) for x in filename]#转换为数字
            filename.sort()
            self.FigureNameList=filename
            self.update('FigNameStart',filename[0])
            self.update('FigNameEnd',filename[-1])
            self.update('FigName',self.FigNameStart)
    def get_dir_tif(self):
        if self.root.Main.FlagDirect:
            return self.root.Main.DirDirect
        else:
            return self.root.Main.generate_fdir()+'/'+str(self.FigName)+'.tif'
    def get_dir_res(self,classname):
        name=''
        if self.root.Main.FlagOther:
            name=self.Other+'_'
        else:
            name='实验编号'+str(self.root.Main.ExpNo)+'_'
        return self.root.Main.generate_fdir()+'/'+name+classname+'.xlsx'
    def save_data(self,data):
        cursor=-1
        for j,i in enumerate(self.data):
            if i[0]==self.FigName:
                cursor=j
                break
        if cursor!=-1:
            self.data[cursor]=[self.FigName,self.FigName*self.Decimate]+data
        else:
            self.data.append([self.FigName,self.FigName*self.Decimate]+data)
            self.data = sorted(self.data, key=lambda x: x[0])
    def delete_data(self,name):
        cursor=-1
        for j,i in enumerate(self.data):
            if i[0]==name:
                cursor=j
                break
        if cursor!=-1:
            self.data.pop(cursor)
        
if __name__=='__main__':
    db=DB()