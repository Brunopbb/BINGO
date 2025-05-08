import tkinter as tk
from tkinter import filedialog, messagebox
import os
import numpy as np
import matplotlib.pyplot as plt
import gc
from datetime import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def parse_time_from_namestr(s):
    return time(hour=int(s[0:2]), minute=int(s[2:4]), second=int(s[4:6]))


def extract_spectra(data_dir, start_str, end_str):
    start_time = time(*map(int, start_str.split(":")))
    end_time = time(*map(int, end_str.split(":")))

    if not os.path.isdir(data_dir):
        raise FileNotFoundError(f"Pasta não encontrada: {data_dir}")

    all_spectra = []
    for fname in sorted(os.listdir(data_dir)):
        if not fname.startswith("Averages_") or not fname.endswith(".npz"):
            continue

        npz_path = os.path.join(data_dir, fname)
        npz_data = np.load(npz_path)

        for npy_key in sorted(npz_data.files):
            try:
                t = parse_time_from_namestr(npy_key)
                if start_time <= t <= end_time:
                    spec = npz_data[npy_key]
                    spec = np.fft.fftshift(spec)
                    all_spectra.append(spec)
            except Exception as e:
                print(f"Erro ao processar {npy_key} em {fname}: {e}")

    if not all_spectra:
        raise ValueError("Nenhum espectro encontrado no intervalo.")

    return np.array(all_spectra)


def gerar_figure(data_, aux2):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    bw = 187.5
    fc = 1120
    fi, ff = fc - bw / 2, fc + bw / 2
    freqs = np.linspace(fi, ff, data_.shape[1])
    epsilon = 1e-12

    ax1.plot(freqs, np.log10(data_[0] + epsilon))
    ax1.set_ylim(0, 5)
    ax1.set(xlabel="Frequency (MHz)", ylabel="Power (Not Calibrated)",
            title=f'Spectrum {fi}-{ff} MHz')

    ax2.set_ylim(ff, fi)
    cax = ax2.imshow(np.log10(aux2.T + epsilon),
                     cmap='viridis', aspect='auto',
                     extent=[0, aux2.shape[0], ff, fi], vmin=0, vmax=5)
    plt.colorbar(cax, ax=ax2, label='Power (Not Calibrated)')

    plt.tight_layout()
    return fig


# --- INTERFACE TKINTER ---
def criar_interface():
    def selecionar_pasta():
        caminho = filedialog.askdirectory()
        if caminho:
            pasta_var.set(caminho)

    def gerar():
        pasta = pasta_var.get()
        inicio = inicio_var.get()
        fim = fim_var.get()

        if not pasta or not inicio or not fim:
            messagebox.showwarning("Campos incompletos", "Preencha todos os campos.")
            return

        try:
            all_spectra = extract_spectra(pasta, inicio, fim)
            fig = gerar_figure(all_spectra[0:1], all_spectra)

            # Limpa canvas anterior
            global canvas
            for child in plot_frame.winfo_children():
                child.destroy()

            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.draw()
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill='both', expand=True)

            global last_fig
            last_fig = fig

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def salvar_como():
        if last_fig is None:
            messagebox.showwarning("Nada para salvar", "Gere um gráfico antes.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile="grafico.png"
        )
        if file_path:
            last_fig.savefig(file_path)
            messagebox.showinfo("Salvo", f"Gráfico salvo em:\n{file_path}")

    root = tk.Tk()
    root.title("Gerador de Espectros")
    root.geometry("1000x700")

    global last_fig
    last_fig = None

    # Layout de entrada
    tk.Label(root, text="Pasta da data (ex: 2025-05-08):").grid(row=0, column=0, sticky="e", pady=5)
    pasta_var = tk.StringVar()
    tk.Entry(root, textvariable=pasta_var, width=50).grid(row=0, column=1, sticky="we")
    tk.Button(root, text="Selecionar...", command=selecionar_pasta).grid(row=0, column=2)

    tk.Label(root, text="Hora início (HH:MM:SS):").grid(row=1, column=0, sticky="e", pady=5)
    inicio_var = tk.StringVar()
    tk.Entry(root, textvariable=inicio_var).grid(row=1, column=1, sticky="we")

    tk.Label(root, text="Hora fim (HH:MM:SS):").grid(row=2, column=0, sticky="e", pady=5)
    fim_var = tk.StringVar()
    tk.Entry(root, textvariable=fim_var).grid(row=2, column=1, sticky="we")

    tk.Button(root, text="Gerar Gráfico", command=gerar, bg="lightgreen").grid(row=3, column=1, pady=10)
    tk.Button(root, text="Salvar Como...", command=salvar_como, bg="lightblue").grid(row=3, column=2, pady=10)

    # Frame para plot
    global plot_frame
    plot_frame = tk.Frame(root, bg="white")
    plot_frame.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

    # Responsividade
    root.grid_rowconfigure(4, weight=1)
    root.grid_columnconfigure(1, weight=1)

    root.mainloop()


if __name__ == "__main__":
    criar_interface()
