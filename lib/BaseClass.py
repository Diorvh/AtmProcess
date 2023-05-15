import tkinter as tk
from tkinter import ttk
class BaseFrame(ttk.Frame):
    def __init__(self,father,**kwargs):
        super().__init__(father,**kwargs)
    def create_var(self,name,back,type='String',init_value=None,FlagSave=False):
        setattr(self,name,getattr(tk,type+'Var')(self))
        setattr(back,name,init_value)
        setattr(back,name+'_front',getattr(self,name))
        if FlagSave:
            getattr(back,'SaveVarName').append(name)
class BaseSubDB:
    def __init__(self,root):
        self.root=root
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
            if hasattr(self,i+'_front'):
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