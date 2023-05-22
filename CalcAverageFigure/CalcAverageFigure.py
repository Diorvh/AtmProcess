import numpy as np
import cv2 as cv
from multiprocessing import Pool
from functools import partial
def calculate_sum(dir,chunk):
    img_list=[]
    for i in chunk:
        img_list.append(cv.imdecode(np.fromfile(file=dir+'/'+str(i)+'.tif',dtype=np.uint8),-1))
    return np.sum(img_list,axis=0,dtype='uint64')
def calculate_average_image(dir,start,end, num_processes):#图片为dir/start.tif-end.tif，全数字，返回uint16的nparray平均值
    chunk_size = (end-start+1) // num_processes
    chunks=[]
    for i in range(num_processes-1):
        chunks.append(list(range(start+i*chunk_size,start+(i+1)*chunk_size)))
    chunks.append(list(range(start+(num_processes-1)*chunk_size,end+1)))

    pool = Pool(processes=num_processes)
    results = pool.map(partial(calculate_sum,dir), chunks)
    pool.close()
    pool.join()
    
    average_image = (np.sum(results, axis=0,dtype='uint64')/(end-start+1)).astype(np.uint16)
    return average_image

if __name__ == '__main__':
    num_processes = 4
    image_list=[]
    for i in range(100000):
        image_list.append(np.ones((2,3),dtype='uint8')*(i+1))
    average_image = calculate_average_image(image_list, num_processes)
    print(average_image)