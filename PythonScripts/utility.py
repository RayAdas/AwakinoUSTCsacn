import scipy
import os, configparser
import numpy as np
from torch.utils.data import Dataset
import torch

class MyFilter:
    def __init__(self):
        self.sample_rate = 1000
        self.cutoff = 60

    def filter(self, waveform, cutoff = None):
        if(cutoff == None):
            cutoff = self.cutoff
        nyquist = 0.5 * self.sample_rate
        normal_cutoff = cutoff / nyquist
        b, a = scipy.signal.butter(4, normal_cutoff, btype='low', analog=False)
        return scipy.signal.filtfilt(b, a, waveform)
    
class FileIO():
    def __init__(self):
        # Load configuration and data
        config_path = os.path.join('.', 'config.ini')
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        py_data_path = self.config['DataSelect']['CurrentDataBase']
        self.algorithm = self.config['AlgorithmSelect']['CurrentAlgorithm']
        py_data_path = os.path.join('.', 'NpWaveData', py_data_path)
        self.datapath = py_data_path

        self.config_metadata = configparser.ConfigParser()
        self.config_metadata.read(os.path.join(py_data_path, 'Metadata.ini'))
        self.waveform_data = np.load(os.path.join(py_data_path, 'waveform_data.npy'))

    def join_datapath(self, path):
        return os.path.join(self.datapath, path)

    def get_metadata(self):
        grid_info = {
            'minX': int(self.config_metadata['Grid']['minX']),
            'minY': int(self.config_metadata['Grid']['minY']),
            'maxX': int(self.config_metadata['Grid']['maxX']),
            'maxY': int(self.config_metadata['Grid']['maxY']),
            'numX': int(self.config_metadata['Grid']['numX']),
            'numY': int(self.config_metadata['Grid']['numY']),
        }
        return grid_info
    
    def get_waveform_data(self):
        return self.waveform_data
    
class Circle:
    def __init__(self):
        self.center = (0, 0)
        self.radius = 0

    def __contains__(self, item: tuple):
        if len(item) != 2:
            raise ValueError("Item must be a tuple of two elements")
        if not all(isinstance(i, (int, float)) for i in item):
            raise ValueError("Item must be a tuple of two numbers")
        return (item[0] - self.center[0])**2 + (item[1] - self.center[1])**2 <= self.radius**2

    def fit(self, points):
        # 将点转换为numpy数组
        points = np.array(points)
        
        # 构造矩阵A和向量b
        A = []
        b = []
        for (x, y) in points:
            A.append([x, y, 1])
            b.append(x**2 + y**2)
        A = np.array(A)
        b = np.array(b)
        
        # 解线性方程组 A * c = b
        c = np.linalg.lstsq(A, b, rcond=None)[0]
        
        # 计算圆心和半径
        x_c = c[0] / 2
        y_c = c[1] / 2
        r = np.sqrt(c[2] + x_c**2 + y_c**2)
        
        self.center = (x_c, y_c)
        self.radius = r

class EchoDataset(Dataset):
    def __init__(self):
        self.data = []
        self.tgt = []

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx], self.tgt[idx]
    
    def load_file(self, file_path):
        dataset_dict = torch.load(file_path)
        self.data = dataset_dict['data']
        self.tgt = dataset_dict['tgt']

if __name__ == "__main__":
    points = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    circle = Circle()
    circle.fit(points)
    print(circle.center, circle.radius)
    print((0, 0) in circle)
    print((1, 1) in circle)
