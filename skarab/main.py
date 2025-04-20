import Tkinter as tk
import ttk
from interface_skarab import skarab_class, RealTimePlot


class MultiSkarabApp(object):


    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de SKARABs")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        skarab_menu = tk.Menu(self.menu, tearoff=0)

        self.menu.add_cascade(label="SKARAB", menu=skarab_menu)
        skarab_menu.add_command(label="Adicionar SKARAB", command=self.adicionar_skarab)
    
    def adicionar_skarab(self):
        popup = tk.Toplevel()
        popup.title("Conectar nova SKARAB")

        tk.Label(popup, text="IP da SKARAB").pack()
        entry_ip = tk.Entry(popup)
        entry_ip.pack()

        def conectar():
            ip = entry_ip.get().strip()
            if ip:
                self.criar_aba_skarab(ip)
                popup.destroy()
        tk.Button(popup, text="Conectar", command=conectar).pack()

    def criar_aba_skarab(self, ip):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text=ip)

        skarab = skarab_class(ip)
        
        RealTimePlot(frame, skarab)


