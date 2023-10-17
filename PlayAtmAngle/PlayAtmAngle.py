import numpy as np
import cv2 as cv
from multiprocessing import Pool
from functools import partial
from lib.lib_AtmAngle import *
def process_calculate_atmangle(dir,settings,chunk):#省内存
    res=[]
    for i in chunk:
        if i%100==0:
            print('正在处理：'+str(i))
        img=cv.imdecode(np.fromfile(file=dir+'/'+str(i)+'.tif',dtype=np.uint8),-1)
        img_calc=65535-img
        #计算
        res0=[i]
        res1=calculate_atmangle(img_calc,settings['XLeft'],settings['XRight'],settings['XMid'],settings['Y'],settings['Thres'])
        res1.append(res1[2]-res1[1])
        res0.extend(res1)
        res.append(res0)
    return res
def mul_calculate_atmangle(dir,start,end,num_processes,settings):
    chunk_size = (end-start+1) // num_processes
    chunks=[]
    for i in range(num_processes-1):
        chunks.append(list(range(start+i*chunk_size,start+(i+1)*chunk_size)))
    chunks.append(list(range(start+(num_processes-1)*chunk_size,end+1)))

    pool = Pool(processes=num_processes)
    results = pool.map(partial(process_calculate_atmangle,dir,settings), chunks)

    pool.close()
    pool.join()
    
    res=[]
    for i in results:
        res.extend(i)
    return res

if __name__ == '__main__':
    num_processes = 4
    image_list=[]
    for i in range(100000):
        image_list.append(np.ones((2,3),dtype='uint8')*(i+1))
    average_image = calculate_average_image(image_list, num_processes)
    print(average_image)