import tkinter as tk
from tkinter import ttk
import cv2 as cv
from lib.lib_tkwidget import *
from lib.ClassFigure import *
from lib.BaseClass import *
from lib.Table import *
import time
from multiprocessing import Pool
from functools import partial
class ClassProcessColorToGray(BaseFrame):#改名
    def __init__(self,father):
        self.father=father
        self.db=father.db
        self.back=self.father.back.ProcessColorToGray#改名
        super().__init__(self.father,padding=5,relief='sunken')
        self.FramePanel=ttk.Frame(self)
        self.FramePanel.grid(row=0,column=0)
        ttk.Button(self.FramePanel,text='开始处理',command=self.CommandButtonProcess).pack(side='left')
    def CommandButtonProcess(self):
        start_time=time.time()
        print('处理中')
        process_color_to_gray(self.db.Main.generate_fdir(),self.db.Main.FrameChoosePic.FigNameStart,self.db.Main.FrameChoosePic.FigNameEnd,self.db.Main.CoreNum)
        print('处理完成，耗时',time.time()-start_time,'秒')

    def FreshSelf(self,img=np.random.randint(0,256,size=(640,704),dtype='uint8')):
        pass

def process(dir,chunk):#省内存
    for i in chunk:
        img=cv.imdecode(np.fromfile(file=dir+'/'+str(i)+'.tif',dtype=np.uint8),-1)
        cv.imencode('.tif', cv.cvtColor(img,cv.COLOR_BGR2GRAY))[1].tofile(dir+'/'+str(i)+'.tif')
def process_color_to_gray(dir,start,end, num_processes):
    chunk_size = (end-start+1) // num_processes
    chunks=[]
    for i in range(num_processes-1):
        chunks.append(list(range(start+i*chunk_size,start+(i+1)*chunk_size)))
    chunks.append(list(range(start+(num_processes-1)*chunk_size,end+1)))

    pool = Pool(processes=num_processes)
    results = pool.map(partial(process,dir), chunks)
    pool.close()
    pool.join()