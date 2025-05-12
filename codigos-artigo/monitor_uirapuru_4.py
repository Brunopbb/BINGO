# -*- coding: utf-8 -*-
import os
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import traceback
import gc

def is_file_stable(file_path, timeout=2):
    start_time = time.time()
    while time.time() - start_time < timeout:
        last_modified_time = os.path.getmtime(file_path)
        time.sleep(0.5)
        if os.path.getmtime(file_path) == last_modified_time:
            return True
    return False

class MyHandler(FileSystemEventHandler):
    def __init__(self, target_file):
        self.target_file = target_file
        self.diretorio = os.path.dirname(target_file)
        self.figure_dir = os.path.join(self.diretorio, 'figure')
        os.makedirs(self.figure_dir, exist_ok=True)

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('realtime.npy'):
            return
        
        print(f"Atualização detectada em: {event.src_path}")

        while not is_file_stable(event.src_path):
            print(f"Aguardando estabilização do arquivo: {event.src_path}")
            time.sleep(1)

        try:
            self.process_file(event.src_path)
        except Exception as e:
            print(f"Erro ao processar {event.src_path}: {e}")
            traceback.print_exc()

    def process_file(self, file_path):
        data = np.load(file_path)
        print(f"Formato do array: {data.shape}")

        aux_path = os.path.join(self.diretorio, 'aux.npy')
        
        if os.path.exists(aux_path):
            aux = np.load(aux_path, allow_pickle=True).reshape((200, 32768))
        else:
            aux = np.zeros((200, 32768))

        data_ = np.zeros((1, 32768))
        data_[0] = np.fft.fftshift(data)
        aux2 = np.concatenate((aux[1:], data_), axis=0)

        self.generate_plots(data_, aux2)
        np.save(aux_path, aux2)

    def generate_plots(self, data_, aux2):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

        bw = 187.5
        fc = 1120
        fi, ff = fc - bw/2, fc + bw/2
        freqs = np.linspace(fi, ff, data_.shape[1])
        epsilon = 1e-12

        ax1.plot(freqs, np.log10(data_[0] + epsilon))
        ax1.set_ylim(0, 5)
        ax2.set_ylim(ff, fi)
        ax1.set(xlabel="Frequency (MHz)", ylabel="Power (Not Calibrated)",
                title=f'Spectrum {fi}-{ff} MHz')

        cax = ax2.imshow(np.log10(aux2.T + epsilon),
                         cmap='viridis', aspect='auto',
                         extent=[0, 200, ff, fi], vmin=0, vmax=5)
        plt.colorbar(cax, ax=ax2, label='Power (Not Calibrated)')

        plt.savefig(os.path.join(self.figure_dir, 'test1.png'))
        plt.close("all")
        gc.collect()

def monitor(base_dir):
    current_observer = None
    last_date = None

    while True:
        current_date = datetime.now().strftime("%Y-%m-%d")
        target_dir = os.path.join(base_dir, current_date)
        target_file = os.path.join(target_dir, 'realtime.npy')

        try:
            os.makedirs(target_dir, exist_ok=True)
            os.makedirs(os.path.join(target_dir, 'figure'), exist_ok=True)

            if current_date != last_date:
                print(f"\n--- Mudança de data detectada: {current_date} ---")

                if current_observer and current_observer.is_alive():
                    try:
                        current_observer.stop()
                        current_observer.join()
                    except Exception as e:
                        print(f"Erro ao parar o observer anterior: {e}")
                        traceback.print_exc()

                event_handler = MyHandler(target_file)
                observer = Observer()
                observer.schedule(event_handler, path=target_dir, recursive=False)
                observer.start()

                current_observer = observer
                last_date = current_date

        except Exception as e:
            print(f"Erro ao configurar diretório para {current_date}: {e}")
            traceback.print_exc()

        time.sleep(1)

if __name__ == "__main__":
    base_directory = '/home/bingo/test_uirapuru'
    monitor(base_directory)

