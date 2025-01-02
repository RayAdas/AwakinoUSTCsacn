import os
import sys
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import configparser

# 定义目录路径
dir_name = '20241226_155137'
NpWaveData_path = '..' + os.sep + 'NpWaveData' + os.sep + dir_name

waveform_data = np.load(NpWaveData_path + os.sep + 'waveform_data.npy')

# 解析Spots.ini文件
ini_path = os.path.join(NpWaveData_path, 'Spots.ini')
config = configparser.ConfigParser()
config.read(ini_path)

spots_num = int(config['Spot']['totality'])
spots_list = []
for i in range(spots_num):
    x = int(config['Xs'][str(i)])
    y = int(config['Ys'][str(i)])
    spots_list.append([x,y])

idxfrom = 0
idxto = 400

for idx, spot in enumerate(spots_list):
    plt.figure(str(spot[0])+','+str(spot[1])+','+str(idx))
    plt.plot(waveform_data[spot[1], spot[0], idxfrom:idxto])
    plt.show()

# idxfrom = 0
# idxto = 400
# tgt_point_x = 3
# tgt_point_y = 21
# plt.figure()
# plt.subplot(4,1,1)
# plt.plot(waveform_data[tgt_point_y-1, tgt_point_x-1, idxfrom:idxto])
# plt.subplot(4,1,2)
# plt.plot(waveform_data[tgt_point_y-1, tgt_point_x, idxfrom:idxto])
# plt.subplot(4,1,3)
# plt.plot(waveform_data[tgt_point_y, tgt_point_x-1, idxfrom:idxto])
# plt.subplot(4,1,4)
# plt.plot(waveform_data[tgt_point_y, tgt_point_x, idxfrom:idxto])
# plt.show()

