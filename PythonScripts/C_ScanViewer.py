import os
import numpy as np
import configparser
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

config_path = os.path.join('.', 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)

py_data_path = config['DataSelect']['CurrentDataBase']
py_data_path = os.path.join('.', 'NpWaveData', py_data_path)

waveform_data = np.load(os.path.join(py_data_path, 'waveform_data.npy'))

# 解析Metadata.ini文件
config_metadata = configparser.ConfigParser()
config_metadata.read(os.path.join(py_data_path, 'Metadata.ini'))

# 读取网格信息
grid_info = {
    'minX': int(config_metadata['Grid']['minX']),
    'minY': int(config_metadata['Grid']['minY']),
    'maxX': int(config_metadata['Grid']['maxX']),
    'maxY': int(config_metadata['Grid']['maxY']),
    'numX': int(config_metadata['Grid']['numX']),
    'numY': int(config_metadata['Grid']['numY']),
}


# 创建主窗口
class WaveformViewer:
    def __init__(self, root, data):
        self.root = root
        self.data = data
        self.current_index = 0

        # 获取数据维度
        self.height, self.width, self.depth = data.shape

        # 计算全局最大最小值
        self.global_min = np.min(data)
        self.global_max = np.max(data)

        # 创建Matplotlib图像
        self.fig, self.ax = plt.subplots()
        self.image = self.ax.imshow(self.data[:, :, self.current_index], cmap='RdBu', vmin=self.global_min, vmax=self.global_max)
        self.ax.set_title(f"Slice: {self.current_index}")
        self.fig.colorbar(self.image, ax=self.ax)

        # 将Matplotlib嵌入到Tkinter窗口
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # 创建滑动条
        self.slider = ttk.Scale(root, from_=0, to=self.depth - 1, orient=tk.HORIZONTAL, command=self.update_plot)
        self.slider.pack(fill=tk.X, padx=10, pady=10)

    def update_plot(self, value):
        self.current_index = int(float(value))  # 确保索引是整数
        self.image.set_data(self.data[:, :, self.current_index])
        self.ax.set_title(f"Slice: {self.current_index}")
        self.canvas.draw()

# 创建Tkinter主窗口
root = tk.Tk()
root.title("Waveform Viewer")
root.geometry("800x600")

# 实例化查看器
viewer = WaveformViewer(root, waveform_data)

# 运行主循环
root.mainloop()
