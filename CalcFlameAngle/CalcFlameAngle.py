import numpy as np
import cv2 as cv
from multiprocessing import Pool
from functools import partial
from MeasureFlameAngle.lib_CalcFlameAngle import *
def Scissor(img,cut):#上下左右
    return img[cut[0]:img.shape[0]-cut[1],cut[2]:img.shape[1]-cut[3]]
def draw_line(img_show,originx,originy,angle,color=(255,255,255),length=1000):
    x2 = int(originx - length * np.cos(angle/180*np.pi))
    y2 = int(originy + length * np.sin(angle/180*np.pi))
    cv.line(img_show,(originx,originy),(x2,y2),color,1)
def process(dir,settings,FlagSave,chunk):#省内存
    res=[]
    savedir=dir+'/伪彩图'
    for i in chunk:
        if i%100==0:
            print('正在处理：'+str(i))
        img=cv.imdecode(np.fromfile(file=dir+'/'+str(i)+'.tif',dtype=np.uint8),-1)
        img_calc=Scissor(img,[settings['ScissorUp'],settings['ScissorDown'],settings['ScissorLeft'],settings['ScissorRight']])
        #计算
        res0=[i]
        res1=calc_theta(img_calc,settings['ImpactX'],settings['ImpactY'],settings['Threshold'])
        res1.append(res1[2]-res1[1])
        res0.extend(res1)
        res2=calc_y(img_calc,settings['Threshold'])
        res2.append(res2[2]-res2[1])
        res0.extend(res2)
        res3=calc_intensty(img_calc,settings['ImpactX'],settings['ImpactY'],
                           res1[1],res1[2],res2[1],res2[2])
        res0.extend(res3)
        res.append(res0)
        #绘图
        if FlagSave:
            if img.dtype=='uint16':
                img_show=np.array(np.round(img/(2**8)),dtype='uint8')
            else:
                img_show=np.array(img,dtype='uint8')
            img_show=(img_show*settings['Gain']).astype('uint8')#增益
            img_show=cv.applyColorMap(img_show,cv.COLORMAP_JET)
            img_show=cv.cvtColor(img_show,cv.COLOR_BGR2RGB)
            img_show=Scissor(img_show,[settings['ScissorUp'],settings['ScissorDown'],settings['ScissorLeft'],settings['ScissorRight']])
            HEIGHT,WIDTH=img_show.shape[0],img_show.shape[1]
            x1,y1=settings['ImpactX'],settings['ImpactY']
            draw_line(img_show,x1,y1,-settings['AngleO']-90,(0,0,255))
            draw_line(img_show,x1,y1,settings['AngleF']-90,(0,0,255))
            draw_line(img_show,x1,y1,-settings['AngleCalc']+90,(0,0,255))
            draw_line(img_show,x1,y1,res1[1],(255,0,0))
            draw_line(img_show,x1,y1,res1[2],(255,0,0))
            draw_line(img_show,x1,y1,res1[0],(0,255,0))
            cv.line(img_show,(0,res2[1]),(WIDTH-1,res2[1]),(255,0,0),1)
            cv.line(img_show,(0,res2[2]),(WIDTH-1,res2[2]),(255,0,0),1)
            cv.line(img_show,(0,res2[0]),(WIDTH-1,res2[0]),(0,255,0),1)
            savefile=cv.cvtColor(img_show,cv.COLOR_RGB2BGR)
            cv.imencode('.tif', savefile)[1].tofile(savedir+'/'+str(i)+'.tif')
    return res
def calc_flame_angle(dir,start,end,num_processes,settings,FlagSave):
    chunk_size = (end-start+1) // num_processes
    chunks=[]
    for i in range(num_processes-1):
        chunks.append(list(range(start+i*chunk_size,start+(i+1)*chunk_size)))
    chunks.append(list(range(start+(num_processes-1)*chunk_size,end+1)))
    savedir=dir+'/伪彩图'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    pool = Pool(processes=num_processes)
    results = pool.map(partial(process,dir,settings,FlagSave), chunks)
    pool.close()
    pool.join()
    
    res=[]
    for i in results:
        res.extend(i)
    return res

if __name__ == '__main__':
    num_processes = 4
    image_list=[]
    for i in range(100000):
        image_list.append(np.ones((2,3),dtype='uint8')*(i+1))
    average_image = calc_flame_angle(image_list, num_processes)
    print(average_image)