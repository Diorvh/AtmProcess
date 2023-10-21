import numpy as np
from scipy.interpolate import griddata
'''
def Interpolate2D(data,x,y,method='linear'):#data是可索引的2Dnp矩阵
    x1,y1,x2,y2=int(np.floor(x)),int(np.floor(y)),int(x)+1,int(y)+1
    points=np.array([[x1,y1],[x1,y2],[x2,y1],[x2,y2]])
    values=np.array([data[x1][y1],data[x1][y2],data[x2][y1],data[x2][y2]])
    xd,yd=np.meshgrid(x,y)#???不知道为什么，总之不能化简
    return griddata(points,values,(xd,yd),method)[0][0]
'''
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
def interpolate2Ddirect(data,x,y):
    x1=int(np.floor(x))
    x2=int(x)+1
    y1=int(np.floor(y))
    y2=int(y)+1
    return (y2-y)/(y2-y1)*((x2-x)/(x2-x1)*data[x1][y1]+(x-x1)/(x2-x1)*data[x2][y1])+(y-y1)/(y2-y1)*((x2-x)/(x2-x1)*data[x1][y2]+(x-x1)/(x2-x1)*data[x2][y2])
if __name__=='__main__':
    # 已知四个点的坐标和对应的函数值
    data=np.array([[0,3],[1,5]])
    # print(interpolate2Ddirect(data,x,x+0.4))#不知道为什么和scipy里面的结果不一致
    print(interpolate2D(data,0.5,1))
