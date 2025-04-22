# -*- coding: utf-8 -*-

import Tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import time
import threading

from odict import odict
import casperfpga
from casperfpga.skarab_definitions import Command, Response, GetSensorDataReq, GetSensorDataResp, SetFanSpeedReq, SetFanSpeedResp
from casperfpga import skarab_definitions as sd


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

    def get_fan_data(self):
        try:
            if not self.skarab:
                return None

            get_sensor_data = GetSensorDataReq()
            response = self.skarab.transport.send_packet(get_sensor_data)

            if not isinstance(response, GetSensorDataResp):
                return None

        
            return odict([
                
                ("rpm", odict([
                ("left_front", response.packet['sensor_data'][0]),
                ("left_middle", response.packet['sensor_data'][1]),
                ("left_back", response.packet['sensor_data'][2]),
                ("right_back", response.packet['sensor_data'][3]),
            ])),
            
            
            ("pwm", odict([
                ("left_front", response.packet['sensor_data'][5] / 100),
                ("left_middle", response.packet['sensor_data'][6] / 100),
                ("left_back", response.packet['sensor_data'][7] / 100),
                ("right_back", response.packet['sensor_data'][8] / 100),
            ]))
        ])

        except Exception as e:
            print "Erro ao adquirir dados dos ventiladores: {}".format(e)
            return False

class RealTimePlot(object):
    def __init__(self, parent, skarab):

        self.skarab_class = skarab
        self.parent = parent
        self.skarab = skarab.skarab  
        self.running = True
        if not self.skarab:
            print("SKARAB não conectada, abortando RealTimePlot.")
            return


        self.tempo_inicial = None
        self.tempos = []

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

        self.time_data = []
        self.start_time = time.time()

        self.update_thread = threading.Thread(target=self.update_plot)
        self.update_thread.daemon = True
        self.update_thread.start()

        #entradas para setar o PWM

        self.pwm_entries = []
        self.pwm_labels = []
        self.pwm_buttons = []
        self.rpm_labels = []
        self.temp_labels = []

        for i in range(4):
            frame = tk.Frame(self.parent)
            frame.pack(pady=2)

            label_nome = tk.Label(frame, text="PWM fan {}".format(i))
            label_nome.pack(side=tk.LEFT)

            entry = tk.Entry(frame, width=5)
            entry.pack(side=tk.LEFT)
            self.pwm_entries.append(entry)

            temp_atual = tk.Label(frame, text=" - Temp Atual: --", width=15, anchor="w")
            temp_atual.pack(side=tk.RIGHT)
            self.temp_labels.append(temp_atual)

            btn = tk.Button(frame, text="Setar", command=lambda idx=i: self.setar_pwm(idx))
            btn.pack(side=tk.LEFT)
            self.pwm_buttons.append(btn)

            pwm_atual = tk.Label(frame, text=" - PWM Atual: --", width=15, anchor="w")
            pwm_atual.pack(side=tk.RIGHT)
            self.pwm_labels.append(pwm_atual)

            rpm_atual = tk.Label(frame, text=" - RPM Atual: --", width=15, anchor="w")
            rpm_atual.pack(side=tk.RIGHT)
            self.rpm_labels.append(rpm_atual)

        

        self.update_pwm_labels()

    def parar(self):
        self.running = False

    def update_plot(self):

        def extract_float(val):
            try:
                if isinstance(val, tuple):
                    return float(val[0])
                elif isinstance(val, str) and " " in val:
                    return float(val.split()[0])
                else:
                    return float(val)
            except:
                return 0.0

        while self.running:
            try:
                if not self.skarab_class.skarab or not self.skarab_class.skarab.transport:
                    time.sleep(1)
                    continue

                transport = self.skarab_class.skarab.transport


                mezz0 = transport.get_sensor_data(sd.sensor_list['mezzanine_site_0_temperature_degC'])
                mezz1 = transport.get_sensor_data(sd.sensor_list['mezzanine_site_1_temperature_degC'])

                now = (time.time() - self.start_time) / 3600.0
                self.time_data.append(now)

                t_fpga = extract_float(mezz1.get("fpga_temperature_degC", "0"))
                t_m1_in = extract_float(mezz1.get("inlet_temperature_degC", "0"))
                t_m1_out = extract_float(mezz1.get("outlet_temperature_degC", "0"))
                t_m1_ctrl = extract_float(mezz1.get("fan_controller_temperature_degC", "0"))
                t_m0_in = extract_float(mezz0.get("inlet_temperature_degC", "0"))
                t_m0_out = extract_float(mezz0.get("outlet_temperature_degC", "0"))
                t_m0_ctrl = extract_float(mezz0.get("fan_controller_temperature_degC", "0"))

                self.temperaturas["fpga_temp"].append(t_fpga)
                self.temperaturas["m1_inlet"].append(t_m1_in)
                self.temperaturas["m1_outlet"].append(t_m1_out)
                self.temperaturas["m1_fan_ctrl"].append(t_m1_ctrl)
                self.temperaturas["m0_inlet"].append(t_m0_in)
                self.temperaturas["m0_outlet"].append(t_m0_out)
                self.temperaturas["m0_fan_ctrl"].append(t_m0_ctrl)

                temps = [t_fpga, t_m1_in, t_m1_out, t_m1_ctrl]
                nomes = ["fpga_temp", "m1_inlet", "m1_outlet", "m1_fan_ctrl"]
                for i in range(len(nomes)):
                    self.temp_labels[i].config(text="{}: {:.1f}°C".format(nomes[i], temps[i]))

                for chave, curva in self.lines.items():
                    curva.set_data(self.time_data, self.temperaturas[chave])

                self.ax.relim()
                self.ax.autoscale_view()
                self.canvas.draw()

            except Exception as e:
                print("Erro ao atualizar temperaturas:", e)

            time.sleep(3)

    def update_fan_status(self):
        fan_data = self.skarab_class.get_fan_data()  
        if fan_data:
            rpm_order = [
                "left_front", 
                "left_middle", 
                "left_back", 
                "right_back"
            ]

            pwm_order = [
                "left_front", 
                "left_middle", 
                "left_back", 
                "right_back"
            ]

            for idx, fan_key in enumerate(rpm_order):
                rpm_value = fan_data['rpm'].get(fan_key, "--")
                self.rpm_labels[idx].config(text="RPM: {}".format(rpm_value))  

            for idx, fan_key in enumerate(pwm_order):
                pwm_value = fan_data['pwm'].get(fan_key, "--")
                self.pwm_labels[idx].config(text="PWM: {}%".format(pwm_value))
        else:
            for label in self.rpm_labels + self.pwm_labels:
                label.config(text="Erro")
    
    def update_pwm_labels(self):
        self.update_fan_status()
        self.parent.after(1000, self.update_pwm_labels)

    def setar_pwm(self, idx):
        try:
            valor_str = self.pwm_entries[idx].get()
            valor = int(valor_str)

            if not (0 <= valor <= 100):
                raise ValueError("O valor do PWM deve estar entre 0 e 100")
            
            set_fan_speed = SetFanSpeedReq(idx, valor)
            if not self.skarab or not self.skarab.transport:
                raise Exception("SKARAB não conectada")

            response = self.skarab.transport.send_packet(set_fan_speed)

            if isinstance(response, SetFanSpeedResp):
                self.pwm_entries[idx].delete(0, tk.END)
                return True
            else:
                return False

        except Exception as e:
            print "Erro ao setar o PWM {}".format(e)
            return False
        
        except ValueError as e:
            print("Erro:", e)
