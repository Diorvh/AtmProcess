import tkinter as tk
from tkinter import ttk
class ScrollableFrame(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        canvas=tk.Canvas(self)
        vbar=tk.Scrollbar(self,orient='vertical',command=canvas.yview)
        vbar.pack(side='right',fill='y')
        hbar=tk.Scrollbar(self,orient='horizontal',command=canvas.xview)
        hbar.pack(side='bottom',fill='x')
        self.scrollable_frame=ttk.Frame(canvas)
        self.scrollable_frame.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0,0),window=self.scrollable_frame,anchor='nw')
        canvas.configure(xscrollcommand=hbar.set,yscrollcommand=vbar.set)
        canvas.pack(fill='both',expand=True)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)),"units")
        canvas.bind_all('<MouseWheel>',_on_mousewheel)
if __name__=='__main__':
    import cv2 as cv
    from PIL import ImageTk,Image
    root=tk.Tk()
    frame=ScrollableFrame(root)
    frame.pack(fill='both',expand=True)
    img=cv.imread(r'E:\20220829235858.png')
    IMG=ImageTk.PhotoImage(Image.fromarray(img))
    tk.Label(frame.scrollable_frame,image=IMG).pack()
    root.mainloop()