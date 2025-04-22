# -*- coding: utf-8 -*-
import Tkinter as tk
from multi_gui import MultiSkarabApp

if __name__ == "__main__":

    root = tk.Tk()
    root.geometry("900x600")              
    root.lift()                           
    root.attributes('-topmost', True)     
    root.after(0, lambda: root.attributes('-topmost', False))  
    app = MultiSkarabApp(root)
    root.mainloop()