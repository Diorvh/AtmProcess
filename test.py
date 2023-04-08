import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import numpy as np

# create a figure and plot some initial data
fig, ax = plt.subplots()
x = np.linspace(0, 10, 100)
y = np.sin(x)
line, = ax.plot(x, y)  # retrieve the Line2D object

# create a Tkinter window
root = tk.Tk()

# create a FigureCanvasTkAgg object and add it to the Tkinter window
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# create a button to update the plot
button = tk.Button(master=root, text="Update")
button.pack(side=tk.BOTTOM)

# define a function to update the plot
def update_plot():
    # update the data
    x_new = np.linspace(0, 20, 200)
    y_new = np.sin(x_new)
    line.set_data(x_new, y_new)  # update the Line2D object
    
    # update the axis limits
    ax.axis([0, 20, -1.5, 1.5])  # set both x and y limits at once
    
    # redraw the canvas
    canvas.draw_idle()

# bind the update function to the button
button.config(command=update_plot)

# start the Tkinter event loop
tk.mainloop()
