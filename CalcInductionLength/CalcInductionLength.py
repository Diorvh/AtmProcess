import numpy as np
from lib.Interpolate2D import *
def calc_graydis_Angle(img,x,y,theta):
    H,W=img.shape
    theta=theta/180*np.pi
    gray=[]
    r=0
    X=x-r*np.cos(theta)
    Y=y+r*np.sin(theta)
    while 0<=X and X<=W-1 and Y<=H-1:
        gray.append(interpolate2D(img,Y,X))
        r+=1
        X=x-r*np.cos(theta)
        Y=y+r*np.sin(theta)
    return np.array(gray)

def calc_graydiff(gray):
    graydiff=[0]
    for i in range(len(gray)-1):
        graydiff.append(gray[i+1]-gray[i])
    return graydiff