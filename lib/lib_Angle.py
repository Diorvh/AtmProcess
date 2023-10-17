import numpy as np
import os,cv2
def calc_angle(img,originx,originy,threshold):#给定图片，原点，阈值，计算一张图片的角度
    img=np.array(img[originy:,:],dtype='uint64')
    sum=np.sum(img)
    l,r,mid=0,np.pi,np.pi/2
    while (np.abs(l-r)>np.pi/1800):
        mid=(l+r)/2
        sum_mid=sum-sum#初始化为0
        for i in range(img.shape[0]):
            cache=int(np.round(originx-i/np.tan(mid)))
            if cache<0:
                cache=0
            elif cache>img.shape[1]:
                cache=img.shape[1]
            sum_mid+=np.sum(img[i,:cache])#不含斜线上的像素点
        if sum_mid>=sum*threshold:
            r=mid
        else:
            l=mid
    return mid/np.pi*180#返回°
def calc_theta(img,originx,originy,threshold):#计算图片的三个角度
    return [calc_angle(img,originx,originy,i) for i in [0.5,threshold,1-threshold]]
def binary_search(l,x):#输入升序序列l，返回第一个>=最大值*x的位置
    a,b,tar=0,len(l)-1,l[-1]*x
    while a<b:
        mid=(a+b)//2
        if l[mid]>=tar:
            b=mid
        else:
            a=mid+1
    return a
def divide_list(l,r_value=0.5):#输入序列l，寻找前x个和>=r_value*总和的位置x
    prefix=[l[0]]
    for i in range(1,len(l)):
        prefix.append(prefix[i-1]+l[i])
    if isinstance(r_value,list):
        return [binary_search(prefix,i) for i in r_value]#支持批量处理
    return binary_search(prefix,r_value)
def calc_y(img,thres):#输入图片，阈值，计算火焰纵向中心、起始、结束位置（我觉得没问题，就计算全场的火焰，originy不影响）
    img=np.array(img,dtype='uint64')
    row_sum=np.sum(img,axis=1)
    return divide_list(row_sum,[0.5,thres,1-thres])
def calc_intensty(img,originx,originy,AngleL,AngleR,YStart,YEnd):
    img=np.array(img,dtype='uint64')
    asum,anum,amax=0,0,0
    for i in range(YStart,YEnd+1):
        lowerbound=int(max(0,np.round(originx-(i-originy)/np.tan(AngleL/180*np.pi))))
        upperbound=int(min(np.round(originx-(i-originy)/np.tan(AngleR/180*np.pi)),img.shape[1]-1))
        asum+=np.sum(img[i,lowerbound:upperbound+1])
        anum+=upperbound-lowerbound+1
        amax=max(amax,np.max(img[i,lowerbound:upperbound+1]))
    return asum/anum,amax
def calc_yavgdis(img,originx,originy,AngleL,AngleR):#返回0-originy之间每行的灰度值平均值（L-R）,火焰锥角内的全场
    img=np.array(img[originy:,:],dtype='uint64')
    y_avg=[]
    for i in range(img.shape[0]):
        lowerbound=max(0,int(np.round(originx-i/np.tan(AngleL/180*np.pi))))
        upperbound=min(int(np.round(originx-i/np.tan(AngleR/180*np.pi))),img.shape[1]-1)
        y_avg.append(np.average(img[i,lowerbound:upperbound+1]))
    return np.array(y_avg)
    
def calc_thetaavgdis(img,originx,originy,AngleL,AngleR,YEnd=None):#返回L-R之间每隔0.1°的灰度值平均值（火焰核心区，yend限制以内）
    img=np.array(img[originy:,:],dtype='uint16')
    # cv2.imshow('Binary Image', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    if YEnd==None:
        YEnd=img.shape[0]
    theta_avg=[]
    for theta in np.arange(round(AngleL,1),round(AngleR,1)+0.1,0.1):
        summ=0
        for y in range(YEnd):
            cache=int(np.round(originx-y/np.tan(theta/180*np.pi)))
            if cache<0 or cache>img.shape[1]-1:
                break
            summ+=img[y,cache]
        theta_avg.append(summ/YEnd)
    return np.array(theta_avg)
if __name__=='__main__':
    length=1000
    img=np.ones([length,length])*65535
    print(calc_angle(img,500,900,0.9))