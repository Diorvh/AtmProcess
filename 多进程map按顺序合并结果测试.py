import numpy as np
import multiprocessing as mp
import time
# 假设array是您的numpy数组
array = np.array(range(int(40)))
# 计算斐波那契数列
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def process_part(args):
    x,array=args
    res=np.zeros((1000,1000))
    for i in array:
        res=fibonacci(37)
    return array+10+x

if __name__ == '__main__':
    num_processes = 24
    x=0
    chunk=np.array_split(array,num_processes)
    print(chunk)
    args_in=[]
    for i in chunk:
        args_in.append((x,i))
    pool = mp.Pool(processes=num_processes)
    start_time=time.time()
    results=pool.map(process_part,args_in)
    pool.close()
    pool.join()
    print("最终结果：", results)
    print('计算完成，耗时',time.time()-start_time,'秒')
