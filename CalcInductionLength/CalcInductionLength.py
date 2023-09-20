import numpy as np
from lib.Interpolate2D import *
def calc_graydis_Angle(img,x,y,angle):
    img=np.array(img[y:,:],dtype='int32')
    H,W=img.shape
    gray=[]
    for i in range(H):
        j=int(np.round(x-i/np.tan(angle/180*np.pi)))
        if j<0 or j>=W:
            break
        gray.append(img[i][j])
    return np.array(gray)
'''def calc_graydis_Angle(img,x,y,angle):#原提取方法
    img=np.array(img[y:,:],dtype='int32')
    H,W=img.shape
    gray=[]
    for i in range(H):
        j=int(np.round(x-i/np.tan(angle/180*np.pi)))
        if j<0 or j>=W:
            break
        gray.append(img[i][j])
    return np.array(gray)'''
def calc_graydiff(gray):
    graydiff=[0]
    for i in range(len(gray)-1):
        graydiff.append(gray[i+1]-gray[i])
    return graydiff