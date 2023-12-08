import cv2 as cv
import numpy as np
from copy import deepcopy
LINE_WIDTH=10
def draw_line(img,originx,originy,angle,color=(255,255,255),length=1000):
    x2 = int(originx - length * np.cos(angle/180*np.pi))
    y2 = int(originy - length * np.sin(angle/180*np.pi))
    cv.line(img,(originx,originy),(x2,y2),color,LINE_WIDTH)
img=cv.imdecode(np.fromfile(file=r'E:\Sci\论文\英文论文\2023.10MMHNTOjet\v6图\1-3-32000.tif',dtype=np.uint8),-1)
img=np.array(np.floor(img/(2**8)),dtype='uint8')
img=cv.cvtColor(img,cv.COLOR_GRAY2RGB)
# img = cv.rotate(img, cv.ROTATE_180)
# img=np.array(img//256,dtype='uint8')
draw_line(img,388,57,90+33.7,(0,0,255))
draw_line(img,388,57,90-46.3,(255,102,51))
cv.line(img,(169,0),(169,767),(0,255,0),LINE_WIDTH)
cv.line(img,(597,0),(597,767),(0,255,0),LINE_WIDTH)
cv.imshow('img',img)
cv.waitKey()
cv.destroyAllWindows()
cv.imencode('.tif', img)[1].tofile(r'E:\Sci\论文\英文论文\2023.10MMHNTOjet\v6图\1-3-32000-绘制.tif')