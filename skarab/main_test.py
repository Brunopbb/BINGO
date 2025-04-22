import tkinter as tk
from mult_janelas import multJanelas
from odict import odict
from matplotlib.figure import Figure



if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x600")
    root.lift()
    app = multJanelas(root)
    root.mainloop()