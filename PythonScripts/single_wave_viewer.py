import numpy as np

# 载入npy文件
data = np.load(r'OSCget/20250722_121511/20250722_121513_1.npy')
import matplotlib.pyplot as plt

plt.plot(data)
plt.xlabel('Sample Index')
plt.ylabel('Voltage')
plt.title('Waveform Visualization')
plt.show()
print(data)