from tkinter import ttk,filedialog
class LabelEntry(ttk.Frame):
    def __init__(self,master,text,var):
        self.root=master
        super().__init__(master)
        ttk.Label(self,text=text+':').pack(side='left')
        ttk.Entry(self,textvariable=var,width=5).pack(side='left')
class LabelLabel(ttk.Frame):
    def __init__(self,master,text,var):
        self.root=master
        super().__init__(master)
        ttk.Label(self,text=text+':').pack(side='left')
        ttk.Label(self,textvariable=var,width=5).pack(side='left')
class ChooseFile(ttk.Frame):
    def __init__(self,master,text,var,width=50,type='file'):
        super().__init__(master)
        ttk.Label(self,text=text).pack(side='left')
        ttk.Entry(self,textvariable=var,width=width).pack(side='left')
        if type=='file':
            ttk.Button(self,text='选择文件',command=lambda:var.set(filedialog.askopenfilename(title='选择文件'))).pack(side='left')
        else:
            ttk.Button(self,text='选择文件夹',command=lambda:var.set(filedialog.askdirectory(title='选择文件夹'))).pack(side='left')
class FrameData(ttk.Frame):
    def __init__(self,master,text,var1,var2):
        super().__init__(master)
        ttk.Label(self,text=text+'=').pack(side='left')
        ttk.Label(self,textvariable=var1).pack(side='left')
        ttk.Label(self,text=',不确定度'+text+'=').pack(side='left')
        ttk.Label(self,textvariable=var2).pack(side='left')
        ttk.Label(self,text='%。').pack(side='left')