import cv2
import glob
import numpy as np
from PIL import Image

# 图片文件夹路径
folder_path = r'E:\实验数据\雾化锥角\20230416\实验编号81\gif'

# 读取所有tif文件
tif_files = glob.glob(f"{folder_path}/*.tif")
# 读取图像并转换为PIL格式
images = []
for file in tif_files:
    img=cv2.imdecode(np.fromfile(file=file,dtype=np.uint8),-1)
    img=np.array(np.floor(img/(2**8)),dtype='uint8')
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    images.append(img_pil)

# 保存为GIF
gif_path = 'output.gif'
images[0].save(gif_path, save_all=True, append_images=images[1:], duration=50, loop=0)
