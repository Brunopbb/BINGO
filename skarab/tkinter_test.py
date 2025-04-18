# -*- coding: utf-8 -*-
import Tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import time

import sys
import struct
from odict import odict
import casperfpga
from casperfpga.skarab_definitions import Command, Response, GetSensorDataReq, GetSensorDataResp, SetFanSpeedReq, SetFanSpeedResp

class skarab_class(object):
    def __init__(self, skarab_ip):
        self.skarab_ip = skarab_ip
        self.skarab = None

    def connect_to_skarab(self):
        if self.skarab == None:
            try:
                self.skarab = casperfpga.CasperFpga(self.skarab_ip)

                if self.skarab.is_connected():
                    print "Skarab conectada."
                    return self.skarab
                else:
                    print "conexão falhou."
                    return None
            except Exception as e:
                print "Erro ao conectar com a SKARAB {}".format(e)
                return None
            
    def set_fan_speed(self, fan_page, pwm_setting):
        try:
            if not (0 <= pwm_setting <= 100):
                raise ValueError("PWM fora do range.")
            

            set_fan_speed = SetFanSpeedReq(fan_page, pwm_setting)

            response = self.skarab.transport.send_packet(set_fan_speed)

            if isinstance(response, SetFanSpeedResp):
                return True
            else:
                return False
        except Exception as e:
            print "Erro ao setar o PWM {}".format(e)
            return False
        
    def get_sensores(self):
        try:

            get_sensor_data = GetSensorDataReq()

            response = self.skarab.transport.send_packet(get_sensor_data)

            if isinstance(response, GetSensorDataResp):
                sensors = odict([
                ("LEFT_FRONT_FAN_PAGE", response.packet['sensor_data'][0]),  
                ("LEFT_MIDDLE_FAN_PAGE", response.packet['sensor_data'][1]),
                ("LEFT_BACK_FAN_PAGE", response.packet['sensor_data'][2]),
                ("RIGHT_BACK_FAN_PAGE", response.packet['sensor_data'][3]),
                ("FPGA_FAN", response.packet['sensor_data'][4]),
                ("left_front_fan_pwm", response.packet['sensor_data'][5] / 100),
                ("left_middle_fan_pwm", response.packet['sensor_data'][6] / 100),
                ("left_back_fan_pwm", response.packet['sensor_data'][7] / 100),
                ("right_back_fan_pwm", response.packet['sensor_data'][8] / 100),
                ("fpga_fan_pwm", response.packet['sensor_data'][9] / 100),

            ])

                return sensors
            else:
                return None
            
        except Exception as e:
            print "Erro ao adquirir os dados do sensores {}".format(e)
            return False

class RealTimePlot(object):
    def __init__(self, root):

        #variaveis para salvar os textos

        text_label_1 = None
        text_label_2 = None
        text_label_3 = None
        text_label_4 = None

        
        #Configurações da figura
        self.root = root
        self.root.title("Temperatura em tempo real")
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Temperatura em tempo real")
        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel(u"Temperatura (°C)")
        self.ax.grid(True)

        #instancia da classe skarab

        #self.skarab = skarab

        #Dados
        self.tempo_inicial = None
        self.tempos = []
        self.temperaturas = []
        self.line, = self.ax.plot([], [], 'r-')

        #Limites do gráfico
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)


        #Converter a figura do matplotlib para widget tkinter

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        #Botao de controle

        self.is_running = False
        self.btn = tk.Button(root, text="Iniciar", command=self.toggle_plot)
        self.btn.pack()


        #entradas para setar o PWM

        self.pwm_entries = []
        self.pwm_labels = []
        self.pwm_buttons = []

        for i in range(4):
            frame = tk.Frame(root)
            frame.pack(pady=2)

            label_nome = tk.Label(frame, text="PWM fan {}".format(i))
            label_nome.pack(side=tk.LEFT)

            entry = tk.Entry(frame, width=5)
            entry.pack(side=tk.LEFT)
            self.pwm_entries.append(entry)

            btn = tk.Button(frame, text="Setar", command=lambda idx=i: self.setar_pwm(idx))
            btn.pack(side=tk.LEFT)
            self.pwm_buttons.append(btn)

            pwm_atual = tk.Label(frame, text="Atual: --")
            pwm_atual.pack(side=tk.LEFT)
            self.pwm_labels.append(pwm_atual)

        
    def setar_pwm(self, idx):
        try:
            valor_str = self.pwm_entries[idx].get()
            valor = int(valor_str)

            if (0 <= valor <= 100):
                raise ValueError("O valor do PWM deve estar entre 0 e 100")
            
                set_fan_speed = setFanSpeedReq(idx, valor)

                response = self.skarab.transport.send_packet(set_fan_speed)

                if insinstance(response, setFanSpeedResp):
                    return True
                else:
                    return False
        except Exception as e:
            print "Erro ao setar o PWM {}".format(e)
            return False

            
            
                
            
        except ValueError as e:
            print("Erro:", e)

    def toggle_plot(self):
        if self.is_running:
            self.is_running = False
            self.btn.config(text="Iniciar")
        else:
            if not self.tempo_inicial:
                self.tempo_inicial = time.time()
            self.is_running = True
            self.btn.config(text="Parar")
            self.update_plot()

    def update_plot(self):
        if self.is_running:

            tempo_atual = time.time() - self.tempo_inicial
            temp_base = 25
            variacao = 10 * np.sin(tempo_atual * 0.1)
            ruido = np.random.normal(0, 0.5)

            nova_temp = temp_base + variacao

            self.tempos.append(tempo_atual)
            self.temperaturas.append(nova_temp)

            if len(self.tempos) > 300:
                self.tempos = self.tempos[-300:]
                self.temperaturas = self.temperaturas[-300:]
                
                

                self.ax.set_xlim(max(0, tempo_atual - 60), max(60, tempo_atual + 5))
                self.ax.set_ylim(
                    min(self.temperaturas[-300:]) - 1 if self.temperaturas else 20,
                    max(self.temperaturas[-300:]) + 1 if self.temperaturas else 40
                )

            self.line.set_data(self.tempos, self.temperaturas)

            self.canvas.show()

            self.root.after(100, self.update_plot)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("teste")
    app = RealTimePlot(root)
    root.mainloop()


