import numpy as np
def interpolate1D(x,x1,y1,x2,y2):#1D线性差值
    if x1==x2:#防止越界
        return y1
    else:
        return (x2-x)/(x2-x1)*y1+(x-x1)/(x2-x1)*y2
def interpolate2D(data,x,y):#用邻近4个网格节点进行双线性插值，用这个
    x1=int(np.floor(x))
    x2=min(int(x)+1,data.shape[0]-1)#防止越界
    y1=int(np.floor(y))
    y2=min(int(y)+1,data.shape[1]-1)#防止越界
    z1=interpolate1D(x,x1,data[x1][y1],x2,data[x2][y1])
    z2=interpolate1D(x,x1,data[x1][y2],x2,data[x2][y2])
    return interpolate1D(y,y1,z1,y2,z2)
npsin,npcos=[],[]
for i in range(1801):
    npsin.append(np.sin((i*0.1+0.05)/180*np.pi))
    npcos.append(np.cos((i*0.1+0.05)/180*np.pi))
def calculate_grayavg_byangle(args):#计算图像两侧的灰度值平均值与梯度，每隔0.1°，采用半径扇形平均
    img,XLeft,XRight,Y,Rmax,ThetaLeft,ThetaRight,NumAvgL,RStartL,NumAvgR,RStartR,IMGThetaLeft,IMGThetaRight=args
    resL=[]#从90°~89.9°到0.1°~0°
    for theta in range(ThetaLeft[0],ThetaLeft[1],-1):
        sumGray=np.int64(0)
        sumS=0
        if abs(theta-IMGThetaLeft)>=NumAvgL:
            r=0
        else:
            r=RStartL
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
        if abs(theta-IMGThetaRight)>=NumAvgR:
            r=0
        else:
            r=RStartR
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
from multiprocessing import Pool
def mul_calculate_atmangle(dirr,START,END,num_processes,XLeft,XRight,Y,Rmax,ThetaLeft,ThetaRight,NumAvgL,RStartL,NumAvgR,RStartR,ThresRatioL,ThresRatioR,window_length,polyorder,FlagSaveImg):
    array=np.array(list(range(START,END+1)))
    chunk=np.array_split(array,num_processes)
    chunk = [x.tolist() for x in chunk]
    args_in=[]
    for i in chunk:
        args_in.append((dirr,i,XLeft,XRight,Y,Rmax,ThetaLeft,ThetaRight,NumAvgL,RStartL,NumAvgR,RStartR,ThresRatioL,ThresRatioR,window_length,polyorder,FlagSaveImg))
    pool = Pool(processes=num_processes)
    results=pool.map(process_calculate_atmangle,args_in)
    pool.close()
    pool.join()
    resL=[]
    resR=[]
    for i in results:
        resL=resL+i[0]
        resR=resR+i[1]
    res=np.column_stack((array,np.array(resL),np.array(resR),np.array(resR)-np.array(resL)))
    return res