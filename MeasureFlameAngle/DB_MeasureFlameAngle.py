from lib.BaseClass import *
import numpy as np
class DB_MeasureFlameAngle(BaseSubDB):
    def __init__(self,root):
        super().__init__(root)
        self.SubClassName=[]
        #后端变量
        self.TableHeadings=['图名称','帧数','宽度/pix','宽度/mm','长度/pix','长度/mm']
    def generate_data(self):
        return [1]
    def generate_title(self):
        return ['上裁剪','下裁剪','左裁剪','右裁剪']
    def generate_FilenameSave(self):#根据所选画图选项
        return 'a'