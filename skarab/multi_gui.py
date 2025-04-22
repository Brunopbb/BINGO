# -*- coding: utf-8 -*-
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

        self.aba_frames = []
        self.plots = []

    def adicionar_skarab(self):
        popup = tk.Toplevel()
        popup.title("Conectar nova SKARAB")

        tk.Label(popup, text="IP da SKARAB").grid(row=0, column=0, padx=5, pady=5)
        entry_ip = tk.Entry(popup)
        entry_ip.grid(row=0, column=1, padx=5, pady=5)

        status_label = tk.Label(popup, text="")
        status_label.grid(row=1, columnspan=2, padx=5, pady=5)

        def conectar():
            ip = entry_ip.get().strip()
            if ip:
                status_label.config(text="Conectando...")
                popup.update()

                skarab = skarab_class(ip)
                obj = skarab.connect_to_skarab()
                if obj is None:
                    status_label.config(text="Erro ao conectar na SKARAB")
                    return

                self.criar_aba_skarab(ip, skarab)
                popup.destroy()

        tk.Button(popup, text="Conectar", command=conectar).grid(row=2, columnspan=2, pady=5)

    def criar_aba_skarab(self, ip, skarab_obj):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text=ip)
        self.notebook.select(len(self.aba_frames))  
        plot = RealTimePlot(frame, skarab_obj)
        self.aba_frames.append(frame)
        self.plots.append(plot)

        btn_fechar = tk.Button(frame, text="Fechar aba", command=lambda idx=len(self.aba_frames)-1: self.fechar_aba(idx))
        btn_fechar.pack(side="bottom", pady=5)

    def fechar_aba(self, idx):
        try:
            frame = self.aba_frames[idx]
            plot = self.plots[idx]

            
            if plot and hasattr(plot, "running"):
                plot.running = False

            if plot and plot.skarab_class and plot.skarab_class.skarab:
                plot.skarab_class.skarab.disconnect()

            self.notebook.forget(frame)
            del self.aba_frames[idx]
            del self.plots[idx]

        except Exception as e:
            print("Erro ao fechar aba:", e)
