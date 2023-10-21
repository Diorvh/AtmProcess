import numpy as np
import cv2 as cv
from multiprocessing import Pool
from lib.lib_AtmAngle import *
import time
# def process_calculate_atmangle(dir,settings,chunk):#省内存
#     res=[]
#     for i in chunk:
#         if i%100==0:
#             print('正在处理：'+str(i))
#         img=cv.imdecode(np.fromfile(file=dir+'/'+str(i)+'.tif',dtype=np.uint8),-1)
#         img_calc=65535-img
#         #计算
#         res0=[i]
#         res1=calculate_atmangle(img_calc,settings['XLeft'],settings['XRight'],settings['XMid'],settings['Y'],settings['Thres'])
#         res1.append(res1[2]-res1[1])
#         res0.extend(res1)
#         res.append(res0)
#     return res
# def mul_calculate_atmangle(dir,start,end,num_processes,settings):
#     chunk_size = (end-start+1) // num_processes
#     chunks=[]
#     for i in range(num_processes-1):
#         chunks.append(list(range(start+i*chunk_size,start+(i+1)*chunk_size)))
#     chunks.append(list(range(start+(num_processes-1)*chunk_size,end+1)))

#     pool = Pool(processes=num_processes)
#     results = pool.map(partial(process_calculate_atmangle,dir,settings), chunks)

#     pool.close()
#     pool.join()
    
#     res=[]
#     for i in results:
#         res.extend(i)
#     return res
def mul_calculate_grayavg_byangle(img,XLeft,XRight,Y,num_processes,Rmax=1000,ThetaLeft=(899,-1),ThetaRight=(901,1801)):
    start_time=time.time()
    chunk_sizeL=int((ThetaLeft[0]-ThetaLeft[1]))//num_processes
    chunk_sizeR=int((ThetaRight[1]-ThetaRight[0]))//num_processes
    chunksL=[]
    chunksR=[]
    for i in range(num_processes-1):
        chunksL.append((ThetaLeft[0]-i*chunk_sizeL,ThetaLeft[0]-(i+1)*chunk_sizeL))
        chunksR.append((ThetaRight[0]+i*chunk_sizeR,ThetaRight[0]+(i+1)*chunk_sizeR))
    chunksL.append((ThetaLeft[0]-(num_processes-1)*chunk_sizeL,ThetaLeft[1]))
    chunksR.append((ThetaRight[0]+(num_processes-1)*chunk_sizeR,ThetaRight[1]))
    args_in=[]
    for i in range(num_processes):
        args_in.append((img,XLeft,XRight,Y,Rmax,chunksL[i],chunksR[i]))
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