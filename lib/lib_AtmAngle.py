import numpy as np
from lib.diff import *
from lib.dft import *
from lib.Interpolate2D import *
npsin,npcos=[],[]
for i in range(1801):
    npsin.append(np.sin((i*0.1+0.05)/180*np.pi))
    npcos.append(np.cos((i*0.1+0.05)/180*np.pi))
#雾化锥角
def calculate_grayavg_byangle(args):#计算图像两侧的灰度值平均值与梯度，每隔0.1°，采用半径扇形平均
    img,XLeft,XRight,Y,Rmax,ThetaLeft,ThetaRight=args
    resL=[]#从90°~89.9°到0.1°~0°
    for theta in range(ThetaLeft[0],ThetaLeft[1],-1):
        sumGray=np.int64(0)
        sumS=0
        r=0
        while (not ((XLeft-(r+0.5)*npcos[theta])<0 or (Y+(r+0.5)*npsin[theta])>img.shape[0]-1)) and (r<=Rmax):#下一个点不越界，同时不超过最大R限制
            S=np.pi*((r+1)**2-r**2)*0.1/360
            CenterX=XLeft-(r+0.5)*npcos[theta]
            CenterY=Y+(r+0.5)*npsin[theta]
            gray=interpolate2D(img,CenterY,CenterX)
            sumGray+=S*gray
            sumS+=S
            r+=1
        resL.append(sumGray/sumS)
    resR=[]#从90°~90.1°到179.9°~180°
    for theta in range(ThetaRight[0],ThetaRight[1]):
        sumGray=np.int64(0)
        sumS=0
        r=0
        while (not ((XRight-(r+0.5)*npcos[theta-1])>img.shape[1]-1 or (Y+(r+0.5)*npsin[theta-1])>img.shape[0]-1)) and (r<=Rmax):#下一个点不越界，同时不超过最大R限制
            S=np.pi*((r+1)**2-r**2)*0.1/360
            CenterX=XRight-(r+0.5)*npcos[theta-1]
            CenterY=Y+(r+0.5)*npsin[theta-1]
            gray=interpolate2D(img,CenterY,CenterX)
            sumGray+=S*gray
            sumS+=S
            r+=1
        resR.append(sumGray/sumS)
    return [np.array(list(range(ThetaLeft[0],ThetaLeft[1],-1)))*0.1+0.05,resL],[np.array(list(range(ThetaRight[0],ThetaRight[1])))*0.1-0.05,resR]#不知道出了什么bug，180.05就是变成901个数字
'''
def calculate_graysum_byangle(img,Xleft,Xright,Y,LowpassFreq):#计算图像两侧的灰度值和与梯度，每隔0.1°计算一个数值
    #最精确的方法就是完全用灰度值的面积积分，针对边界上每种情况都要讨论，进行三角形或者四边形的双线性插值函数积分，非常复杂
    #这里先用计算不超过的方法进行计算
    #!!!特定角度出现极高幅值干扰，必须还是得用精确方法!!!
    YEnd=img.shape[0]#计算域Y结束值
    resL=[]#从90°到0°
    for theta in np.arange(90,-0.1,-0.1):
        summ=np.int64(0)
        for y in range(Y,YEnd):
            X=int(np.ceil(Xleft-(y-Y)/np.tan(theta/180*np.pi)))#向右侧取整，尽量少的点
            if X<0:#越界需要修正
                X=0
            summ+=np.sum(img[y][X:Xleft+1])
        resL.append(summ)
    resLdiff=diff(resL)
    resLdiff=AmpFilter(resLdiff[::-1],LowpassFreq)[::-1]# resLdiff=lowpass(resLdiff,len(resLdiff),LowpassFreq)
    resLdiff2=diff(resLdiff)
    resR=[]#从90°到180°
    for theta in np.arange(90,180.1,0.1):
        summ=np.int64(0)
        for y in range(Y,YEnd):
            X=int(np.floor(Xright-(y-Y)/np.tan(theta/180*np.pi)))#向左侧取整，尽量少的点
            if X>img.shape[1]-1:#越界需要修正
                X=img.shape[1]-1
            summ+=np.sum(img[y][Xright:X+1])
        resR.append(summ)
    resRdiff=diff(resR)
    resRdiff=AmpFilter(resRdiff[::-1],LowpassFreq)[::-1]
    # resRdiff=lowpass(resRdiff,len(resRdiff),LowpassFreq)
    resRdiff2=diff(resRdiff)
    return [np.arange(90,-0.1,-0.1),resL],[np.arange(90,180.1,0.1),resR],[np.arange(89.9,-0.1,-0.1),resLdiff],[np.arange(90.1,180.1,0.1),resRdiff],[np.arange(89.8,-0.1,-0.1),resLdiff2],[np.arange(90.2,180.1,0.1),resRdiff2]
def calc_atmangle(img,Xleft,Xright,Y,Rstart,Rend):#计算图像两侧的灰度值和随角度（0.1°)的梯度，最大梯度的位置被认为是雾化锥角位置
    pass
def calculate_atmangle(img,XLeft,XRight,XMid,Y,thres):
    WIDTH=img.shape[1]
    if XMid<WIDTH/2:
        img=img[:,:XMid*2+1]
    else:
        offset=2*XMid-WIDTH+1
        img=img[:,offset:]
        XLeft+=offset
        XRight+=offset
        XMid+=offset
    resL=[np.arange(round(0.1,1),round(89.9,1)+0.1,0.1),calc_thetaavgdis(img,XLeft,Y,0.1,89.9,400)]
    resR=[np.arange(round(90.1,1),round(179.9,1)+0.1,0.1),calc_thetaavgdis(img,XRight,Y,90.1,179.9,400)]
    return resL,resR
def calculate_atmangle2(img,XLeft,XRight,XMid,Y,thres):#灰度值加权二分查找，已发现有问题：同一工况下，雾化锥角越来越大
    WIDTH=img.shape[1]
    if XMid<WIDTH/2:
        img=img[:,:XMid*2+1]
    else:
        offset=2*XMid-WIDTH+1
        img=img[:,offset:]
        XLeft+=offset
        XRight+=offset
        XMid+=offset
    return [calc_angle(img,XMid,Y,0.5),calc_angle(img,XLeft,Y,thres),calc_angle(img,XRight,Y,1-thres)]
'''