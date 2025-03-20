import scipy
import os, configparser
import numpy as np

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
        py_data_path = os.path.join('.', 'NpWaveData', py_data_path)
        self.config_metadata = configparser.ConfigParser()
        self.config_metadata.read(os.path.join(py_data_path, 'Metadata.ini'))
        self.waveform_data = np.load(os.path.join(py_data_path, 'waveform_data.npy'))

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