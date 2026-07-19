import numpy as np
from ImageProcessv3.lib.Interpolate2D import interpolate2D
def calc_angle(img,originx,originy,threshold):#给定图片，原点，阈值，计算一张图片的角度
    img=np.array(img[originy:,:],dtype='uint64')
    total_intensity=np.sum(img)
    l,r,mid=0,np.pi,np.pi/2
    while (np.abs(l-r)>np.pi/1800):
        mid=(l+r)/2
        sum_mid=0
        for i in range(img.shape[0]):
            cache=int(np.round(originx-i/np.tan(mid)))
            if cache<0:
                cache=0
            elif cache>img.shape[1]:
                cache=img.shape[1]
            sum_mid+=np.sum(img[i,:cache])#不含斜线上的像素点
        if sum_mid>=total_intensity*threshold:
            r=mid
        else:
            l=mid
    return mid/np.pi*180#返回°
def calc_theta(img,originx,originy,threshold):#计算图片的三个角度
    return [calc_angle(img,originx,originy,i) for i in [0.5,threshold,1-threshold]]

def find_threshold_positions(arr, threshold1, threshold2):
    """
    Finds two positions in a given array such that:
    - Position a is where the sum of elements from the 0th to the ath element is closest to threshold1 of the total sum.
    - Position b is where the sum of elements from the 0th to the bth element is closest to threshold2 of the total sum.

    Parameters:
    arr (numpy array): The input array.
    threshold1 (float): The first threshold.
    threshold2 (float): The second threshold.

    Returns:
    int, int: Positions a and b.
    """
    total_sum = np.sum(arr)

    def find_closest_position(threshold):
        cumulative_sum = np.cumsum(arr)
        ratios = cumulative_sum / total_sum
        closest_position = np.argmin(np.abs(ratios - threshold))
        return closest_position

    position_a = int(find_closest_position(threshold1))
    position_b = int(find_closest_position(threshold2))

    return [position_a, position_b]
def calc_Rparameter(img,X,Y,Threshold,thetaL,thetaR):#计算图像在thetaL和thetaR之间的灰度值和，然后按照面积阈值提取火焰起点和终点
    theta=np.arange(thetaL, thetaR, 0.1)+0.05
    res=np.zeros(1000,dtype='double')
    for i in theta:
        npcos=np.cos(i/180*np.pi)
        npsin=np.sin(i/180*np.pi)
        r=1
        CenterX=X-(r-0.5)*npcos
        CenterY=Y+(r-0.5)*npsin
        while CenterX>=0 and CenterX<=img.shape[1]-1 and CenterY<=img.shape[0]-1:#下一个点不越界
            # S=np.pi*(r**2-(r-1)**2)*0.1/360 #灰度值和，已经验证过非常不合理
            S=1#求每个R上的平均值
            gray=interpolate2D(img,CenterY,CenterX)
            res[r]+=gray*S
            r+=1
            CenterX=X-(r-0.5)*npcos
            CenterY=Y+(r-0.5)*npsin
    res=np.trim_zeros(res,'b')#此处为光强沿R分布
    return find_threshold_positions(res,Threshold,1-Threshold)
def calc_graydis_flamedirection(img,x,y,theta):#计算火焰方向上的灰度值分布
    H,W=img.shape
    npcos=np.cos(theta/180*np.pi)
    npsin=np.sin(theta/180*np.pi)
    gray=[]
    r=0
    X=x-r*npcos
    Y=y+r*npsin
    while 0<=X and X<=W-1 and Y<=H-1:
        gray.append(interpolate2D(img,Y,X))
        r+=1
        X=x-r*npcos
        Y=y+r*npsin
    return np.array(gray)
def calc_Rparameter_flamedirection(img,X,Y,Threshold,theta):#只计算火焰方向上的强度
    gray=calc_graydis_flamedirection(img,X,Y,theta)
    return find_threshold_positions(gray,Threshold,1-Threshold)
    
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
