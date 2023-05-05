from lib_json import *
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
class BaseSubDB:
    def __init__(self):
        self.SubClassName=[]
        self.SaveVarName=[]
    def update(self,name,value,FlagFresh=True):
        setattr(self,name,value)
        if FlagFresh:#刷新前端
            getattr(self,name+'_front').set(value)
        if hasattr(self,'update_'+name):#调用其他触发命令
            getattr(self,'update_'+name)()
    def get(self,name):
        return getattr(self,name)
    def load(self,dict):
        for i in self.SaveVarName:
            setattr(self,i,dict[i])
            getattr(self,i+'_front').set(dict[i])
        for i in self.SubClassName:
            getattr(self,i).load(dict)
    def save(self):
        dict={}
        for i in self.SaveVarName:
            dict[i]=getattr(self,i)
        for i in self.SubClassName:
            dict={**dict,**getattr(self,i).save()}
        return dict
class DB_main(BaseSubDB):
    def __init__(self,root):
        self.root=root
        self.SubClassName=['FrameChoosePic']
        self.SaveVarName=['DirData','ExpNo','FDirRes']
        self.FrameChoosePic=DB_FrameChoosePic(self.root)
        self.DirData=''
        self.ExpNo=0
        self.FDirRes=''
class DB_FrameChoosePic(BaseSubDB):
    def __init__(self,root):
        self.root=root
        self.SubClassName=[]
        self.SaveVarName=['Decimate']
        self.Decimate=0

if __name__=='__main__':
    #db.update('NumPipe',1)
    db=DB()