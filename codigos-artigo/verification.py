import numpy as np
import matplotlib.pyplot as plt

data = np.load("/home/brunoee/Documents/dados/2025-05-10/Averages_0548.npz")

aux_d = data["054835"].copy()


aux_d[25385:25502] += 1000
aux_d[30273:30347] += 10000



data_ = np.zeros((1, 32768))
data_[0] = np.fft.fftshift(aux_d)



aux = np.zeros((1, 32768))
aux2 = np.concatenate((aux, data_), axis=0)


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

cax = ax2.imshow(np.log10(data_.T + epsilon),
                cmap='viridis', aspect='auto',
                extent=[0, 200, ff, fi], vmin=0, vmax=5)
plt.colorbar(cax, ax=ax2, label='Power (Not Calibrated)')


plt.show()