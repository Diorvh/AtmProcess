from lib_json import *
import os
from BaseClass import *
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
        filename=os.listdir(self.root.Main.DirData+'/实验编号'+str(self.root.Main.ExpNo))
        filename=[x for x in filename if not x.endswith('.chd')]#删除以.chd结尾的名称
        filename=[int(x[:-4]) for x in filename]#转换为数字
        filename.sort()
        self.FigureNameList=filename
        self.update('FigNameStart',filename[0])
        self.update('FigNameEnd',filename[-1])
        self.update('FigName',self.FigNameStart)
    def get_dir(self):
        return self.root.Main.DirData+'/实验编号'+str(self.root.Main.ExpNo)+'/'+str(self.FigName)+'.tif'
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
if __name__=='__main__':
    db=DB()