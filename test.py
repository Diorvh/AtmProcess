import cv2 as cv
import numpy as np
dir=r'E:\实验数据\雾化锥角\20230812\实验编号20\7000.tif'
dir2=r'E:\实验数据\雾化锥角\20230812\实验编号20\70000.tif'
img=cv.imdecode(np.fromfile(file=dir,dtype=np.uint8),-1)
print(img)
cv.imencode('.tif', img)[1].tofile(dir2)
