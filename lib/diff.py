def diff(y):
    ydiff=[]
    for i in range(1,len(y)):
        ydiff.append(y[i]-y[i-1])
    return ydiff