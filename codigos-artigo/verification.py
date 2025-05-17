import numpy as np
import matplotlib.pyplot as plt

data = np.load("/home/brunoee/Documents/dados/2025-05-10/Averages_0548.npz")

data_ = np.zeros((1, 32768))
data_[0] = np.fft.fftshift(data["054835"])

print(data_)

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
plt.show()