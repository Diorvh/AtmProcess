import tkinter as tk
from tkinter import ttk
import numpy as np

class TableFrame(ttk.Frame):
    def __init__(self, parent, headings):
        super().__init__(parent)
        self.table = None
        self.headings = headings
        self._create_widgets()

    def _create_widgets(self):
        # Create the table
        self.table = ttk.Treeview(self, columns=self.headings, show="headings")
        self.table.grid(column=0, row=0, sticky="nsew")
        # Add the headings
        for col_name in self.headings:
            self.table.heading(col_name, text=col_name)
            self.table.column(col_name, width=100)
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

class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Table Example")
        self.geometry("400x300")
        self.headings = ["Name", "Age", "Gender"]
        self.table_frame = TableFrame(self, self.headings)
        self.table_frame.grid(column=0, row=0, sticky="nsew")
        self.button = tk.Button(self, text="Update Table", command=self.update_table)
        self.button.grid(column=0, row=1)

    def update_table(self):
        data = np.random.rand(20, 3)
        self.table_frame.update_table(data)

if __name__ == "__main__":
    app = MyApp()
    app.mainloop()