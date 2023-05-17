# import json
# from lib_json import *
# dict={}
# dict['a']=[1,2,3,4,[5.123123123]]
# dict['b']='dijojf'
# dict['c']='C:\idjfisf\sdifjsds.sidjf'
# write_json(r'D:\Transfer\SciCodes\撞击喷嘴雾化\图像处理\file.json',dict)
# print(read_json(r'D:\Transfer\SciCodes\撞击喷嘴雾化\图像处理\file.json'))

# dict1={'a':[1,2,2,3,3],'b':'sdfaf'}
# dict2={'a':[1,2],'c':0.5}
# dict3={**dict1,**dict2}
# print(dict3)

# a='100.tif'
# print(a[:-1])

# import cv2 as cv
# import numpy as np
# # img=cv.imdecode(np.fromfile(file=r'D:\Transfer\testdata\实验编号69\20.tif',dtype=np.uint16),-1)
# img=cv.imdecode(np.fromfile(file=r'E:\20230224\jet\AverageFigure\Origin\2-1-37000-43000-ClassAverageFigure.tif',dtype=np.uint8),-1)
# print(img.dtype)
# print(np.max(img))
# cv.imshow('image',img)
# cv.waitKey(0)
# cv.destroyAllWindows()

import tkinter as tk
from tkinter import ttk

def on_page_changed(event):
    selected_tab = event.widget.select()
    current_page_name = event.widget.tab(selected_tab, "text")
    print("Current page changed to:", current_page_name)

# Create a tkinter window
window = tk.Tk()

# Create a Notebook widget
notebook = ttk.Notebook(window)

# Create pages in the Notebook
page1 = tk.Frame(notebook)
page2 = tk.Frame(notebook)
page3 = tk.Frame(notebook)

# Add pages to the Notebook
notebook.add(page1, text="Page 1")
notebook.add(page2, text="Page 2")
notebook.add(page3, text="Page 3")

# Bind the page change event
notebook.bind("<<NotebookTabChanged>>", on_page_changed)

# Pack or grid the Notebook widget
notebook.pack(expand=True, fill=tk.BOTH)  # Or use grid if preferred

# Run the tkinter event loop
window.mainloop()
