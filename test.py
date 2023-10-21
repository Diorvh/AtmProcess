import numpy as np
import time
N=int(2e7)
start_time=time.time()
for i in range(N):
    a=np.sin(69.5/180*np.pi)
print('计算完成1，耗时',time.time()-start_time,'秒')
start_time=time.time()
for i in range(N):
    a=69.5/180*np.pi
print('计算完成2，耗时',time.time()-start_time,'秒')