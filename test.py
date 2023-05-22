import tkinter as tk
from tkinter import ttk
# import json
# from lib_json import *
# dict={}
# dict['a']=[1,2,3,4,[5.123123123]]
# dict['b']='dijojf'
# dict['c']='C:\idjfisf\sdifjsds.sidjf'
# write_json(r'D:\Transfer\SciCodes\撞击喷嘴雾化\图像处理\file.json',dict)
# print(read_json(r'D:\Transfer\SciCodes\撞击喷嘴雾化\图像处理\file.json'))

# dict1={'a':[1,2,2,3,3],'b':'sdfaf'}
# dict2={'a':[1,2],'c':0.5}
# dict3={**dict1,**dict2}
# print(dict3)

# a='100.tif'
# print(a[:-1])

# import cv2 as cv
# import numpy as np
# # img=cv.imdecode(np.fromfile(file=r'D:\Transfer\testdata\实验编号69\20.tif',dtype=np.uint16),-1)
# img=cv.imdecode(np.fromfile(file=r'E:\20230224\jet\AverageFigure\Origin\2-1-37000-43000-ClassAverageFigure.tif',dtype=np.uint8),-1)
# print(img.dtype)
# print(np.max(img))
# cv.imshow('image',img)
# cv.waitKey(0)
# cv.destroyAllWindows()



# def printentry(value):
#     print(a.get(),' ',value)
# root=tk.Tk()
# a=tk.IntVar(root)
# e=ttk.Entry(root,textvariable=a)
# e.pack()
# e.bind('<Return>',printentry)
# root.mainloop()

# import cv2 as cv
# import numpy as np
# img=cv.imdecode(np.fromfile(file=r'D:\20220224_jet\test-1\26000.tif',dtype=np.uint8),-1)
# cv.imencode('.tif', img)[1].tofile(r'D:\20220224_jet\test-1\26001.tif')

# def CommandCheckButton():
#     print(FlagExpNo.get())
# def CommandButton():
#     FlagExpNo.set(not FlagExpNo.get())
# root=tk.Tk()
# FlagExpNo=tk.BooleanVar(root)
# cb=ttk.Checkbutton(root,onvalue=True,offvalue=False,variable=FlagExpNo,command=CommandCheckButton)
# cb.pack()
# et=ttk.Entry(root)
# et.pack()
# bt=ttk.Button(root,command=CommandButton)
# bt.pack()
# root.mainloop()

import cv2
import numpy as np
from multiprocessing import Pool

# List of images (2D numpy arrays)
image_list = [np.array([[0, 0, 0], [255, 255, 255]], dtype=np.uint8),
              np.array([[255, 0, 0], [0, 255, 0]], dtype=np.uint8),
              np.array([[0, 0, 255], [255, 0, 255]], dtype=np.uint8),
              np.array([[0, 0, 255], [255, 0, 255]], dtype=np.uint8)]


def calculate_average_image(images, num_processes):
    # Convert the list of images to a numpy array
    image_array = np.array(images)

    # Calculate the chunk size for parallel processing
    chunk_size = len(image_array) // num_processes

    # Create a pool of processes
    pool = Pool(processes=num_processes)

    # Map the image chunks to worker processes
    chunks = [image_array[i:i+chunk_size] for i in range(0, len(image_array), chunk_size)]
    results = pool.map(calculate_chunk_average, chunks)

    # Close the pool of processes
    pool.close()
    pool.join()

    # Combine the results to calculate the overall average image
    average_image = np.mean(results, axis=0)#.astype(np.uint8)

    return average_image


def calculate_chunk_average(chunk):
    # Calculate the average image for a chunk of images
    return np.mean(chunk, axis=0)


if __name__ == '__main__':
    num_processes = 2  # Number of processes for parallel execution

    # Calculate the average image using parallel processing
    average_image = calculate_average_image(image_list, num_processes)

    # Display the average image
    print(average_image)
