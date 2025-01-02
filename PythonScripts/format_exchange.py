import os
import configparser
import numpy as np

# 定义目录路径
dir_name = '20241226_155137'
dir_path = '../OSCget/' + dir_name

# 解析index.ini文件
ini_path = os.path.join(dir_path, 'index.ini')
config = configparser.ConfigParser()
config.read(ini_path)

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
waveform_data = np.zeros((grid_info['numY'], grid_info['numX'], 999), dtype=float)

# 遍历每条数据并读取波形数据
for y in range(grid_info['numY']):
    section = str(y)
    if section in config:
        for x in range(grid_info['numX']):
            file_path = config[section][str(x)]
            file_path = file_path.replace('\\', os.sep)  # 转换为操作系统路径分隔符
            
            # 使用 np.loadtxt 读取波形数据文件
            waveform_data[y, x] = np.loadtxt(file_path, delimiter=',')
            
output_path = '..' + os.sep + 'NpWaveData' + os.sep + dir_name

if not os.path.exists(output_path):
    os.makedirs(output_path)
np.save(output_path + os.sep + 'waveform_data.npy', waveform_data)

config_out = configparser.ConfigParser()
config_out.add_section('Grid')
config_out.set('Grid','minX',config['Grid']['minX'])
config_out.set('Grid','minY',config['Grid']['minY'])
config_out.set('Grid','maxX',config['Grid']['maxX'])
config_out.set('Grid','maxY',config['Grid']['maxY'])
config_out.set('Grid','numX',config['Grid']['numX'])
config_out.set('Grid','numY',config['Grid']['numY'])

with open(output_path + os.sep + 'Grid.ini', 'w') as configfile:
    config_out.write(configfile)