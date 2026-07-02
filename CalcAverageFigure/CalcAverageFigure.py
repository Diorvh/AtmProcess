import numpy as np
import cv2 as cv
import multiprocessing,os
from multiprocessing import Pool
from functools import partial
from lib.lib_mulprocess import *
from core.image_io import read_image, write_tiff
def calculate_sum(dir,chunk):#省内存
    try:
        sum=np.zeros(read_image(dir+'/'+str(chunk[0])+'.tif').shape,dtype='uint64')
        for i in chunk:
            sum+=read_image(dir+'/'+str(i)+'.tif')
        return sum
    except Exception as e:
        print(f"Error: {e}")
        # Check if the process is still alive before termination
        current_process = multiprocessing.current_process()
        if current_process.is_alive():
            # Check if process has a _popen attribute before terminating
            if hasattr(current_process, '_popen') and current_process._popen is not None:
                current_process._popen.terminate()
                current_process._popen.wait()  # Wait for the process to complete

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

def process(dir,chunk):#省内存
    try:
        for i in chunk:
            img=read_image(dir+'/'+str(i)+'.tif')
            write_tiff(dir+'/'+str(i)+'.tif', cv.cvtColor(img,cv.COLOR_BGR2GRAY))
    except Exception as e:
        print(f"Error: {e}")
        # Check if the process is still alive before termination
        current_process = multiprocessing.current_process()
        if current_process.is_alive():
            # Check if process has a _popen attribute before terminating
            if hasattr(current_process, '_popen') and current_process._popen is not None:
                current_process._popen.terminate()
                current_process._popen.wait()  # Wait for the process to complete


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
def process_DAVIS_images(folder_path,filelist):#预处理DAVIS导出的图像
    # 遍历文件夹中的所有文件
    for filename in filelist:
        if filename.endswith(".tif"):
            # 构建完整的文件路径
            filepath = os.path.join(folder_path, filename)
            
            # 去除前缀B和前导0
            new_filename = filename.lstrip("B").lstrip("0")
            # 使用OpenCV读取图像
            img=read_image(filepath)
            
            # 将图像每个像素点的灰度值乘以16
            img = img * 16
            
            # 保存处理后的图像
            write_tiff(os.path.join(folder_path, new_filename), img)
            # 删除旧图像
            os.remove(filepath)
def mul_process_DAVIS_images(folder_path,num_processes):
    filelist=os.listdir(folder_path)
    chunks=split_list(filelist,num_processes)
    
    pool=Pool(processes=num_processes)
    results=pool.map(partial(process_DAVIS_images,folder_path),chunks)
    pool.close()
    pool.join()
if __name__ == '__main__':
    num_processes = 4
    image_list=[]
    for i in range(100000):
        image_list.append(np.ones((2,3),dtype='uint8')*(i+1))
    average_image = calculate_average_image(image_list, num_processes)
    print(average_image)
