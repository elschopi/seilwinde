import numpy as np
import matplotlib.pyplot as plt

x_times = []
y_volt = []
y_amp = []
y_pow = []

data = np.genfromtxt('messwerte_reihe5_160720.csv', delimiter=',', usecols=(2, 3, 4), names=True)
times = np.genfromtxt('messwerte_reihe5_160720.csv',delimiter=',',usecols=(1),names=True, dtype=None, encoding=None)

x_times = []
y_volt = []
y_amp = []
y_pow = []

for line in times:
    x_times.append(line[0])

for line in data:
    y_volt.append(line[0])
    y_amp.append(line[1])
    y_pow.append(line[2])

plt.plot(x_times, y_volt, label='Spannung')
plt.plot(x_times, y_amp, label='Strom')
plt.plot(x_times, y_pow, label='Leistung')
plt.ylabel('V / A / W')
plt.title('Versuchsgraph')
plt.legend()
plt.show()
