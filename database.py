from lib.lib_json import *
from lib.BaseClass import *
from MeasureSheet_Manual.DB_MeasureSheet import *
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
class DB_FrameChoosePic(BaseSubDB):
    def __init__(self,root):
        super().__init__(root)
        self.SubClassName=['MeasureSheet']
        self.MeasureSheet=DB_MeasureSheet(self.root)
        #后端变量
        self.FigureNameList=[]
        self.data=[]
        # self.SaveVarName.append('FigureNameList')#保存
    def Fresh(self):#update_FigureNameList
        if False:#self.root.Main.FlagDirGenerate:
            filename=os.listdir(self.root.Main.DirData)
        else:
            filename=os.listdir(self.root.Main.DirData+'/实验编号'+str(self.root.Main.ExpNo))
        filename=[x for x in filename if x.endswith('.tif')]#只保留tif结尾的
        filename=[int(x[:-4]) for x in filename]#转换为数字
        filename.sort()
        self.FigureNameList=filename
        self.update('FigNameStart',filename[0])
        self.update('FigNameEnd',filename[-1])
        self.update('FigName',self.FigNameStart)
    def get_dir_tif(self):
        if False:
            return self.root.Main.DirData+'/'+str(self.FigName)+'.tif'
        else:
            return self.root.Main.DirData+'/实验编号'+str(self.root.Main.ExpNo)+'/'+str(self.FigName)+'.tif'
    def get_dir_res(self,classname):
        if False:
            return self.root.Main.DirData+'/'+classname+'.xlsx'
        else:
            return self.root.Main.DirData+'/实验编号'+str(self.root.Main.ExpNo)+'/实验编号'+str(self.root.Main.ExpNo)+'_'+classname+'.xlsx'
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
if __name__=='__main__':
    db=DB()