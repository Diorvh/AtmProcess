import numpy as np
from multiprocessing import Pool
from functools import partial
from lib.lib_Angle import *
import cv2 as cv
def Scissor(img,cut):#上下左右
    return img[cut[0]:img.shape[0]-cut[1],cut[2]:img.shape[1]-cut[3]]
def process(dir,settings,chunk):#省内存
    res=[]
    for i in chunk:
        if i%10==0:
            print('已完成：'+str((i-chunk[0])/len(chunk)*100)+'%')
        img=cv.imdecode(np.fromfile(file=dir+'/'+str(i)+'.tif',dtype=np.uint8),-1)
        img_calc=Scissor(img,[settings['ScissorUp'],settings['ScissorDown'],settings['ScissorLeft'],settings['ScissorRight']])
        #计算
        res0=[i]
        res1=calc_theta(img_calc,settings['ImpactX'],settings['ImpactY'],settings['Threshold'])
        res1.append(res1[2]-res1[1])
        res0.extend(res1)
        res2=calc_Rparameter_flamedirection(img_calc,settings['ImpactX'],settings['ImpactY'],settings['Threshold'],res1[0])
        res2.append(res2[1]-res2[0])
        res0.extend(res2)
        res.append(res0)
    return res
def calc_flame_angle(dir,start,end,num_processes,settings):
    chunk_size = (end-start+1) // num_processes
    chunks=[]
    for i in range(num_processes-1):
        chunks.append(list(range(start+i*chunk_size,start+(i+1)*chunk_size)))
    chunks.append(list(range(start+(num_processes-1)*chunk_size,end+1)))
    pool = Pool(processes=num_processes)
    results = pool.map(partial(process,dir,settings), chunks)
    pool.close()
    pool.join()
    
    res=[]
    for i in results:
        res.extend(i)
    return res
