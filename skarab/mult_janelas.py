import tkinter as tk
import tkinter.ttk as ttk
from skarab_class_test import skarab_class
from skarab_class_test import plotRealTime
import time
class multJanelas():

    def __init__(self, root):
        self.root = root
        self.root.title("Testando")


        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)


        self.skarab_menu = tk.Menu(self.menu, tearoff=0)
        self.skarab_menu.add_command(label="Adicionar SKARAB", command=self.adicionar_skarab)

        self.skarab_menu_2 = tk.Menu(self.menu, tearoff=0)
        self.skarab_menu_2.add_command(label="Teste")

        self.menu.add_cascade(label="SKARAB", menu=self.skarab_menu)
        self.menu.add_cascade(label="Info", menu=self.skarab_menu_2)


        self.aba_frames = []
        self.plots = []

    def adicionar_skarab(self):

        popup = tk.Toplevel()
        popup.title("Add SKARAB")

        tk.Label(popup, text="IP SKARAB").grid(row=0, column=0, padx=5, pady=5)
        entry_ip = tk.Entry(popup)
        entry_ip.grid(row=0, column=1, padx=5, pady=5)

        info_label = tk.Label(popup, text="dsad")
        info_label.grid(row=1, columnspan=2, padx=5, pady=5)

        

        def conectar():
            ip = entry_ip.get()
            if ip:
                skarab = skarab_class(ip)
                conn = skarab.conectar_skarab()
                if conn is None:
                    info_label.config(text=f"Erro ao conectar")
                    return 
            
                self.cria_aba(skarab, ip)
                popup.destroy()

            
        btn_connect = tk.Button(popup, text="Conectar", command=conectar)
        btn_connect.grid(row=2, columnspan=2)

    def cria_aba(self, skarab, ip):

        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text=ip)
        self.notebook.select(len(self.aba_frames))
        plot = plotRealTime(frame, skarab)
        self.aba_frames.append(frame)
        self.plots.append(plot)

        




    

        

        
        