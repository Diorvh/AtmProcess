import numpy as np
from lib.diff import *
from lib.dft import *
from lib.Interpolate2D import *
from scipy.signal import savgol_filter
#雾化锥角
def calculate_grayavg_byangle(args):#计算图像两侧的灰度值平均值与梯度，每隔0.1°，采用半径扇形平均
    img,XLeft,XRight,Y,Rmax,ThetaLeft,ThetaRight,NumAvgL,RStartL,NumAvgR,RStartR=args
    resL=[]#从90°~89.9°到0.1°~0°
    for theta in range(ThetaLeft[0],ThetaLeft[1]-1,-1):
        sumGray=np.int64(0)
        sumS=0
        r=0
        npsin=np.sin((theta*0.1+0.05)/180*np.pi)
        npcos=np.cos((theta*0.1+0.05)/180*np.pi)
        if (theta-ThetaLeft[1])>=NumAvgL:#目前只对批量计算生效，单张不能使用，否则单张计算会出问题
            r=0
        else:
            r=RStartL
        CenterX=XLeft-(r+0.5)*npcos
        CenterY=Y+(r+0.5)*npsin
        while (not (CenterX<0 or CenterY>img.shape[0]-1)) and (r<=Rmax):#下一个点不越界，同时不超过最大R限制
            S=np.pi*(2*r+1)*0.1/360
            gray=interpolate2D(img,CenterY,CenterX)
            sumGray+=S*gray
            sumS+=S
            r+=1
            CenterX=XLeft-(r+0.5)*npcos
            CenterY=Y+(r+0.5)*npsin
        resL.append(sumGray/sumS)
    resR=[]#从90°~90.1°到179.9°~180°
    for theta in range(ThetaRight[0],ThetaRight[1]):
        sumGray=np.int64(0)
        sumS=0
        r=0
        npsin=np.sin((theta*0.1+0.05)/180*np.pi)
        npcos=np.cos((theta*0.1+0.05)/180*np.pi)
        if -(theta-ThetaRight[1])>=NumAvgR:
            r=0
        else:
            r=RStartR
        
        CenterX=XRight-(r+0.5)*npcos
        CenterY=Y+(r+0.5)*npsin
        while (not (CenterX>img.shape[1]-1 or CenterY>img.shape[0]-1)) and (r<=Rmax):#下一个点不越界，同时不超过最大R限制
            S=np.pi*(2*r+1)*0.1/360
            gray=interpolate2D(img,CenterY,CenterX)
            sumGray+=S*gray
            sumS+=S
            r+=1
            CenterX=XRight-(r+0.5)*npcos
            CenterY=Y+(r+0.5)*npsin
        resR.append(sumGray/sumS)
    return [np.array(list(range(ThetaLeft[0],ThetaLeft[1],-1)))*0.1+0.05,resL],[np.array(list(range(ThetaRight[0],ThetaRight[1])))*0.1+0.05,resR]#不知道出了什么bug，180.05就是变成901个数字
def calculate_atm_angle_thres_p2(args):#输入参数和grayavg_byangle，直接给出雾化锥角
    resL,resR,NumAvgL,NumAvgR,ThresRatioL,ThresRatioR,window_length,polyorder=args
    #先用原始曲线计算阈值
    cache_max=np.average(resL[1][:NumAvgL])
    cache_min=np.average(resL[1][-NumAvgL:])
    ThresL=cache_min+(cache_max-cache_min)*ThresRatioL
    cache_max=np.average(resR[1][:NumAvgR])
    cache_min=np.average(resR[1][-NumAvgR:])
    ThresR=cache_min+(cache_max-cache_min)*ThresRatioR
    #再到滤波后的曲线中去找,找到滤波后曲线最接近阈值的元素的位置
    resLSG=[resL[0],savgol_filter(resL[1],window_length,polyorder)]
    resRSG=[resR[0],savgol_filter(resR[1],window_length,polyorder)]
    # AngleLPos=np.abs(resLSG[1]-ThresL).argmin()
    # AngleRPos=np.abs(resRSG[1]-ThresR).argmin()
    #优化：找到最接近中心的，第一个小于0的元素索引
    AngleLPos=find_last_greater_equal(resLSG[1],ThresL)
    AngleRPos=find_last_greater_equal(resRSG[1],ThresR)
    #更新
    return resL[0][AngleLPos],resR[0][AngleRPos]
def calculate_atm_angle_thres(args):#输入图片和参数，直接给出雾化锥角
    img,XLeft,XRight,Y,Rmax,ThetaLeft,ThetaRight,NumAvgL,RStartL,NumAvgR,RStartR,ThresRatioL,ThresRatioR,window_length,polyorder=args
    resL,resR=calculate_grayavg_byangle((img,XLeft,XRight,Y,Rmax,(899,ThetaLeft),(900,ThetaRight),NumAvgL,RStartL,NumAvgR,RStartR))
    return calculate_atm_angle_thres_p2((resL,resR,NumAvgL,NumAvgR,ThresRatioL,ThresRatioR,window_length,polyorder))
def find_last_greater_equal(arr, thres):
    """
    找到从右往左第一个大于等于阈值的元素的位置

    参数:
    arr (np.array): 输入的一维NumPy数组
    thres (int or float): 阈值

    返回:
    int: 从右往左第一个大于等于阈值的元素的位置，如果不存在返回-1
    """
    reversed_arr = arr[::-1]  # 反转数组
    indices = np.where(reversed_arr >= thres)[0]
    if indices.size > 0:
        last_index = arr.size - indices[0] - 1  # 计算从右往左的索引
        return last_index
    else:
        return -1
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