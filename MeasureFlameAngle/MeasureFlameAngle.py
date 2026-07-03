import numpy as np
from multiprocessing import Pool
from functools import partial
from lib.lib_Angle import *
import cv2 as cv
from core.image_io import read_image
from core.parallel import split_frame_range
def Scissor(img,cut):#上下左右
    return img[cut[0]:img.shape[0]-cut[1],cut[2]:img.shape[1]-cut[3]]
def process(dir,settings,chunk):#省内存
    res=[]
    for i in chunk:
        if i%10==0:
            print('已完成：'+str((i-chunk[0])/len(chunk)*100)+'%')
        img=read_image(dir+'/'+str(i)+'.tif')
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
    chunks=split_frame_range(start,end,num_processes)
    pool = Pool(processes=len(chunks))
    results = pool.map(partial(process,dir,settings), chunks)
    pool.close()
    pool.join()
    
    res=[]
    for i in results:
        res.extend(i)
    return res
