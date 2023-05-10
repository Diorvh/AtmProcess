import numpy as np
def read_txt(fdir):
    data=[]
    with open(fdir,'r') as f:
        odata=f.readlines()
    for i in odata:
        cache=i.strip().split('\t')
        try:
            data.append(list(map(float,cache)))
        except:
            data.append(cache)
    return [data[10:12],np.array(data[12:])]#标题和数据分开