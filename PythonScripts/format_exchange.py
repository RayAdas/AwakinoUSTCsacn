"""
@discription: 读取USTCscan产生的txt文件, 转换为numpy格式
"""

import os
import configparser
import numpy as np

config_path = os.path.join('.', 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)

src_data_path = config['DataSelect']['CurrentDataBase']
src_data_path = os.path.join('.', 'OSCget', src_data_path)
py_data_path = config['DataSelect']['CurrentDataBase']
py_data_path = os.path.join('.', 'NpWaveData', py_data_path)

# 解析index.ini文件
index_path = os.path.join(src_data_path, 'index.ini')
config = configparser.ConfigParser()
config.read(index_path)

# 读取网格信息
grid_info = {
    'minX': int(config['Grid']['minX']),
    'minY': int(config['Grid']['minY']),
    'maxX': int(config['Grid']['maxX']),
    'maxY': int(config['Grid']['maxY']),
    'numX': int(config['Grid']['numX']),
    'numY': int(config['Grid']['numY']),
}

# 初始化存储波形数据的numpy数组
waveform_data = np.zeros((grid_info['numY'], grid_info['numX'], 1000), dtype=float)

# 遍历每条数据并读取波形数据
for y in range(grid_info['numY']):
    section = str(y)
    if section in config:
        for x in range(grid_info['numX']):
            file_path = config[section][str(x)]
            file_path = os.path.join(src_data_path, file_path)
            
            # 使用 np.loadtxt 读取波形数据文件
            w = np.loadtxt(file_path, delimiter=',')
            if len(w) < 1000:
                w = np.pad(w, (0, 1000 - len(w)), 'constant')
            else:
                w = w[:1000]
            waveform_data[y, x] = w

if not os.path.exists(py_data_path):
    os.makedirs(py_data_path)
np.save(os.path.join(py_data_path, 'waveform_data.npy'), waveform_data)

config_out = configparser.ConfigParser()
config_out.add_section('Grid')
config_out.set('Grid','minX',config['Grid']['minX'])
config_out.set('Grid','minY',config['Grid']['minY'])
config_out.set('Grid','maxX',config['Grid']['maxX'])
config_out.set('Grid','maxY',config['Grid']['maxY'])
config_out.set('Grid','numX',config['Grid']['numX'])
config_out.set('Grid','numY',config['Grid']['numY'])

with open(os.path.join(py_data_path, 'Metadata.ini'), 'w') as configfile:
    config_out.write(configfile)