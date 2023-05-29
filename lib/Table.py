import tkinter as tk
from tkinter import ttk
import numpy as np

class TableFrame(ttk.Frame):
    def __init__(self, parent, headings, visible_rows=40):
        super().__init__(parent)
        self.table = None
        self.headings = headings
        self.visible_rows = visible_rows
        self._create_widgets()

    def _create_widgets(self):
        # Create the table
        self.table = ttk.Treeview(self, columns=self.headings, show="headings")
        self.table.grid(column=0, row=0, sticky="nsew")
        # Set the height to control the number of visible rows
        self.table['height'] = self.visible_rows
        # Add the headings
        for col_name in self.headings:
            self.table.heading(col_name, text=col_name)
            self.table.column(col_name, width=60)
        # Add a vertical scrollbar
        yscrollbar = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
        yscrollbar.grid(column=1, row=0, sticky="ns")
        self.table.configure(yscrollcommand=yscrollbar.set)

    def update_table(self, data):
        if self.table is None:
            raise ValueError("Table not initialized!")
        # Clear previous data
        self.table.delete(*self.table.get_children())
        # Add new data
        if data is not None:
            for row in data:
                self.table.insert("", "end", values=list(row))
        # Set the scrollbar to the bottom
        self.table.yview_moveto(1.0)

    def update_headings(self, new_headings):
        if self.table is None:
            raise ValueError("Table not initialized!")
        column_widths={}
        for col_name in self.headings:
            column_widths[col_name]=self.table.column(col_name,'width')
        # Update the headings
        self.headings = new_headings
        self.table["columns"] = self.headings
        for col_name in self.headings:
            self.table.heading(col_name, text=col_name)
        def restore_column_widths():
            for col_name,width in column_widths.items():
                self.table.column(col_name, width=width)
                print('update column')
        self.after(10000,restore_column_widths)

class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Table Example")
        self.geometry("400x300")
        self.headings = ["Name", "Age", "Gender"]
        self.table_frame = TableFrame(self, self.headings,10)
        self.table_frame.grid(column=0, row=0, sticky="nsew")
        self.button = tk.Button(self, text="Update Table", command=self.func)
        self.button.grid(column=0, row=1)
    def func(self):
        self.table_frame=TableFrame(self, self.headings,10)
    def update_table(self):
        data = np.random.rand(20, 3)
        self.table_frame.update_table(data)

if __name__ == "__main__":
    app = MyApp()
    app.mainloop()