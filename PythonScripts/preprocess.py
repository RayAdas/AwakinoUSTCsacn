
import numpy as np
from scipy.signal import hilbert, find_peaks
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QApplication, QVBoxLayout, QSlider, QLabel, QWidget, QHBoxLayout
from PySide6.QtCore import Qt
from utility import MyFilter, FileIO
from PyEMD import EMD

class WaveformApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Waveform Viewer")

        self.mf = MyFilter()
        self.fio = FileIO()
        grid_info = self.fio.get_metadata()
        self.waveform_data = self.fio.get_waveform_data()

        self.numX = grid_info['numX']
        self.numY = grid_info['numY']
        
        # Initialize UI components
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Add waveform display
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Add sliders and labels
        slider_layout = QHBoxLayout()

        self.x_slider = self.create_slider(0, self.numX - 1, 0, "X Index")
        self.y_slider = self.create_slider(0, self.numY - 1, 0, "Y Index")
        self.cutoff_slider = self.create_slider(1, 500, 50, "Cutoff Frequency (Hz)")

        slider_layout.addWidget(self.x_slider['label'])
        slider_layout.addWidget(self.x_slider['slider'])
        slider_layout.addWidget(self.y_slider['label'])
        slider_layout.addWidget(self.y_slider['slider'])
        slider_layout.addWidget(self.cutoff_slider['label'])
        slider_layout.addWidget(self.cutoff_slider['slider'])

        layout.addLayout(slider_layout)
        self.setLayout(layout)

        self.update_waveform()

    def create_slider(self, min_val, max_val, init_val, label_text):
        label = QLabel(f"{label_text}: {init_val}")
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(init_val)
        slider.valueChanged.connect(self.update_waveform)
        return {'label': label, 'slider': slider}

    def update_waveform(self):
        x_index = self.x_slider['slider'].value()
        y_index = self.y_slider['slider'].value()
        cutoff = self.cutoff_slider['slider'].value()

        self.x_slider['label'].setText(f"X Index: {x_index}")
        self.y_slider['label'].setText(f"Y Index: {y_index}")
        self.cutoff_slider['label'].setText(f"Cutoff Frequency (Hz): {cutoff}")

        waveform = self.waveform_data[x_index, y_index, :]

        self.mf.cutoff = cutoff
        DCcutted_waveform = waveform - np.mean(waveform) # 去除直流分量
        filtered_waveform = self.mf.filter(DCcutted_waveform)
        envelope = np.abs(hilbert(filtered_waveform))

        # 局部峰值检测
        # peaks, _ = find_peaks(abs(filtered_waveform), height=0)  # 仅保留大于0的峰值
        # envelope = np.interp(np.arange(len(abs(filtered_waveform))), peaks, abs(filtered_waveform)[peaks])

        # 取绝对值然后滤波
        # self.mf.cutoff = cutoff
        # envelope = self.mf.filter(np.abs(filtered_waveform))

        # 取绝对值然后移动平均
        # envelope = np.convolve(np.abs(filtered_waveform), np.ones(100)/100, mode='same')

        # 经验模态分解
        # emd = EMD()
        # envelope = emd(filtered_waveform)

        self.ax.clear()
        self.ax.plot(waveform, label='Original Waveform')
        self.ax.plot(filtered_waveform, label='Filtered Waveform')
        self.ax.plot(envelope, label='Envelope')
        self.ax.legend()
        self.ax.set_title(f"Waveform at X={x_index}, Y={y_index}")
        self.canvas.draw()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    viewer = WaveformApp()
    viewer.resize(800, 600)
    viewer.show()
    sys.exit(app.exec_())
