
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk

class skarab_class():

    def __init__(self, skarab_ip):
        self.skarab_ip = skarab_ip
        self.skarab = None

        self.ip_list = ["10.42.1.152", "10.42.0.73", "10.42.1.153"]

    def conectar_skarab(self):
        
        if self.skarab_ip in self.ip_list:
            self.skarab = "Aqui existe uma skarab"
            return self.skarab
        return self.skarab



class plotRealTime():

    def __init__(self, parent, skarab):
        self.skarab_class = skarab
        self.parent = parent
    

        #Configurações da figura
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Temperatura em tempo real")
        self.ax.set_xlabel("Tempo (h)")
        self.ax.set_ylabel(u"Temperatura (°C)")
        self.ax.grid(True)

        self.temperaturas = {
            "fpga_temp": [],
            "m1_inlet": [],
            "m1_outlet": [],
            "m1_fan_ctrl": [],
            "m0_inlet": [],
            "m0_outlet": [],
            "m0_fan_ctrl": [],
        }

        self.lines = {
            "fpga_temp": self.ax.plot([], [], label="FPGA Temp", color="red")[0],
            "m1_inlet": self.ax.plot([], [], label="M1 Inlet", color="blue")[0],
            "m1_outlet": self.ax.plot([], [], label="M1 Outlet", color="cyan")[0],
            "m1_fan_ctrl": self.ax.plot([], [], label="M1 Fan Ctrl", color="magenta")[0],
            "m0_inlet": self.ax.plot([], [], label="M0 Inlet", color="green")[0],
            "m0_outlet": self.ax.plot([], [], label="M0 Outlet", color="orange")[0],
            "m0_fan_ctrl": self.ax.plot([], [], label="M0 Fan Ctrl", color="purple")[0],
        }

        self.ax.legend(loc="upper right")

        #Converter a figura do matplotlib para widget tkinter

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)