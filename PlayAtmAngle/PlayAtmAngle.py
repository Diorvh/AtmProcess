import numpy as np
import cv2 as cv
from multiprocessing import Pool
from lib.lib_AtmAngle import *
import os
from core.image_io import read_image, write_tiff
def draw_line(img,originx,originy,angle,color=(255,255,255),length=1000):
    x2 = int(originx - length * np.cos(angle/180*np.pi))
    y2 = int(originy + length * np.sin(angle/180*np.pi))
    cv.line(img,(originx,originy),(x2,y2),color,1)
def process_calculate_atmangle(args):#省内存
    dirr,NAME,XLeft,XRight,Y,Rmax,ThetaLeft,ThetaRight,NumAvgL,RStartL,NumAvgR,RStartR,ThresRatioL,ThresRatioR,window_length,polyorder,FlagSaveImg=args
    resL=[]
    resR=[]
    for i in NAME:
        if i%100==0:
            print('正在处理：'+str(i))
        img=read_image(dirr+'/'+str(i)+'.tif')
        a,b=calculate_atm_angle_thres((65535-img,XLeft,XRight,Y,Rmax,ThetaLeft,ThetaRight,NumAvgL,RStartL,NumAvgR,RStartR,ThresRatioL,ThresRatioR,window_length,polyorder))
        resL.append(a)
        resR.append(b)
        if FlagSaveImg:
            if len(img.shape)==2:
                img=cv.cvtColor(img,cv.COLOR_GRAY2RGB)
            MAX=65535 if np.max(img)>255 else 255
            img=cv.ellipse(img,(XLeft,Y),(Rmax,Rmax),0,90,180-ThetaLeft*0.1,(0,0,MAX),1)
            img=cv.ellipse(img,(XRight,Y),(Rmax,Rmax),0,180-ThetaRight*0.1,90,(0,0,MAX),1)
            draw_line(img,XLeft,Y,a,(MAX,0,0))
            draw_line(img,XRight,Y,b,(MAX,0,0))
            if not os.path.exists(dirr+'/处理结果'):
                os.makedirs(dirr+'/处理结果')
            write_tiff(dirr+'/处理结果/'+str(i)+'.tif', img)
    return resL,resR
def mul_calculate_atmangle(dirr,START,END,num_processes,XLeft,XRight,Y,Rmax,ThetaLeft,ThetaRight,NumAvgL,RStartL,NumAvgR,RStartR,ThresRatioL,ThresRatioR,window_length,polyorder,FlagSaveImg):
    array=np.array(list(range(START,END+1)))
    chunk=np.array_split(array,num_processes)
    chunk = [x.tolist() for x in chunk]
    args_in=[]
    for i in chunk:
        args_in.append((dirr,i,XLeft,XRight,Y,Rmax,ThetaLeft,ThetaRight,NumAvgL,RStartL,NumAvgR,RStartR,ThresRatioL,ThresRatioR,window_length,polyorder,FlagSaveImg))

    pool = Pool(processes=num_processes)
    results=pool.map(process_calculate_atmangle,args_in)
    pool.close()
    pool.join()
    resL=[]
    resR=[]
    for i in results:
        resL=resL+i[0]
        resR=resR+i[1]
    res=np.column_stack((array,np.array(resL),np.array(resR),np.array(resR)-np.array(resL)))
    return res

def mul_calculate_grayavg_byangle(img,num_processes,XLeft,XRight,Y,Rmax,ThetaLeft,ThetaRight,NumAvgL,RStartL,NumAvgR,RStartR):
    num_processes=6
    chunk_sizeL=int(899-ThetaLeft)//num_processes
    chunk_sizeR=int(ThetaRight-900)//num_processes
    chunksL=[]
    chunksR=[]
    for i in range(num_processes-1):
        chunksL.append((899-i*chunk_sizeL,899-(i+1)*chunk_sizeL+1))#为了兼容分角度和分图片，所以+1
        chunksR.append((900+i*chunk_sizeR,900+(i+1)*chunk_sizeR))
    chunksL.append((899-(num_processes-1)*chunk_sizeL,ThetaLeft))
    chunksR.append((900+(num_processes-1)*chunk_sizeR,ThetaRight))
    args_in=[]
    for i in range(num_processes):
        args_in.append((img,XLeft,XRight,Y,Rmax,chunksL[i],chunksR[i],NumAvgL,RStartL,NumAvgR,RStartR))
    pool = Pool(processes=num_processes)
    results = pool.map(calculate_grayavg_byangle,args_in)
    pool.close()
    pool.join()
    resL1,resL2=results[0][0][0],results[0][0][1]
    resR1,resR2=results[0][1][0],results[0][1][1]
    for i in range(1,num_processes):
        resL1=np.concatenate((resL1,results[i][0][0]))
        resL2=np.concatenate((resL2,results[i][0][1]))
        resR1=np.concatenate((resR1,results[i][1][0]))
        resR2=np.concatenate((resR2,results[i][1][1]))
    return [resL1,resL2],[resR1,resR2]

if __name__ == '__main__':
    num_processes = 4
    image_list=[]
    for i in range(100000):
        image_list.append(np.ones((2,3),dtype='uint8')*(i+1))
    img=cv.imdecode(np.fromfile(file=r'E:\实验数据\雾化锥角\20230416\实验编号1\6400.tif',dtype=np.uint8),-1)
    print(mul_calculate_grayavg_byangle(img,273,303,103,24))
