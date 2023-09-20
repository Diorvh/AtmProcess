import numpy as np
from scipy.interpolate import griddata

def Interpolate2D(data,x,y,method='linear'):#data是可索引的2Dnp矩阵
    x1,y1,x2,y2=int(np.floor(x)),int(np.floor(y)),int(np.ceil(x)),int(np.ceil(y))
    points=np.array([[x1,y1],[x1,y2],[x2,y1],[x2,y2]])
    values=np.array([data[x1][y1],data[x1][y2],data[x2][y1],data[x2][y2]])
    xd,yd=np.meshgrid(x,y)#???不知道为什么，总之不能化简
    return griddata(points,values,(xd,yd),method)[0][0]

if __name__=='__main__':
    # 已知四个点的坐标和对应的函数值
    data=[[0,3],
          [1,5]]
    print(Interpolate2D(data,0.5,0.5))
