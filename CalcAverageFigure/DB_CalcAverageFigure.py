from lib.BaseClass import *
import numpy as np
class DB_CalcAverageFigure(BaseSubDB):#改名
    def __init__(self,root):
        super().__init__(root)
        self.SubClassName=[]
        #后端变量
        self.TableHeadings=[]
    def generate_data(self):
        return []
    def generate_title(self):
        return []
    def Fresh(self):
        self.update('FigStart',self.root.Main.FrameChoosePic.FigNameStart)
        self.update('FigEnd',self.root.Main.FrameChoosePic.FigNameEnd)