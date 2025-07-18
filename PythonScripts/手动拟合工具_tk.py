import sys
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import Label
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from scipy.constants import pi
import pandas as pd
from scipy import signal
from collections import namedtuple


EchoInfo = namedtuple('EchoInfo', ['fc', 'tau', 'phi','alpha', 'beta', 'r'])
TANH_M = 1e12
echo1 = EchoInfo(2.5e6,0,0,2e12,1,0)

# 中央频率（Hz）
f0 = 2.1e6
f_low = 1e6
f_high = 3e6
order = 4  # 滤波器阶数
# 采样率（Hz）
fs = 1e8

b, a = signal.butter(order, [f_low / (fs / 2), f_high / (fs / 2)], btype='band')

w, h = signal.freqz(b, a, worN=4096, fs=fs)
gd = signal.group_delay((b, a), w=w, whole=True)

def echo_function(t,
                  tau,
                  beta,
                  fc = echo1.fc,
                  phi = echo1.phi,
                  alpha = echo1.alpha,
                  r = echo1.r):
    global TANH_M
    env = beta * np.exp(-alpha * (1 - r * np.tanh(TANH_M * (t - tau))) * (t - tau) ** 2)
    s = env * np.cos(2 * np.pi * fc * (t - tau) + phi)
    return s

def rsSum(src,A,phi):
    global echo1
    j = 0
    for i in src:
        altY = echo_function(t=i[0], beta=A, tau=phi)
        src[j][1] += altY
        j += 1

class ManualFitTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Waveform Slider (Tkinter)')
        self.geometry('900x700')
        self.create_widgets()
        self.update_plot()

    def create_widgets(self):
        # Sliders and labels
        self.slider_phi_1 = tk.Scale(self, from_=0, to=1400, orient=tk.HORIZONTAL, label='Phi1 (x1e-8)', command=lambda e: self.update_plot())
        self.slider_phi_1.set(0)
        self.slider_phi_1.grid(row=0, column=0, sticky='ew')
        self.label_phi_1 = Label(self, text='Phi1 Value: 0e-8')
        self.label_phi_1.grid(row=0, column=1)

        self.slider_phi_2 = tk.Scale(self, from_=0, to=1400, orient=tk.HORIZONTAL, label='Phi2 (x1e-8)', command=lambda e: self.update_plot())
        self.slider_phi_2.set(0)
        self.slider_phi_2.grid(row=0, column=2, sticky='ew')
        self.label_phi_2 = Label(self, text='Phi2 Value: 0e-8')
        self.label_phi_2.grid(row=0, column=3)

        self.slider_A_1 = tk.Scale(self, from_=0, to=1000, orient=tk.HORIZONTAL, label='A1 (x1e-3)', command=lambda e: self.update_plot())
        self.slider_A_1.set(0)
        self.slider_A_1.grid(row=1, column=0, sticky='ew')
        self.label_A_1 = Label(self, text='A1 Value: 0')
        self.label_A_1.grid(row=1, column=1)

        self.slider_A_2 = tk.Scale(self, from_=0, to=1000, orient=tk.HORIZONTAL, label='A2 (x1e-3)', command=lambda e: self.update_plot())
        self.slider_A_2.set(0)
        self.slider_A_2.grid(row=1, column=2, sticky='ew')
        self.label_A_2 = Label(self, text='A2 Value: 0')
        self.label_A_2.grid(row=1, column=3)

        self.label_err = Label(self, text='Err Value: 0')
        self.label_err.grid(row=2, column=0, columnspan=4)

        # Matplotlib Figure
        self.fig, self.ax = plt.subplots(figsize=(8,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=3, column=0, columnspan=4, sticky='nsew')
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

    def update_plot(self):
        slider_phi_1_value = self.slider_phi_1.get()
        slider_A_1_value = self.slider_A_1.get()
        self.label_phi_1.config(text=f"Phi1 Value: {slider_phi_1_value}e-8")
        self.label_A_1.config(text=f"A1 Value: {slider_A_1_value / 1000}")
        slider_phi_2_value = self.slider_phi_2.get()
        slider_A_2_value = self.slider_A_2.get()
        self.label_phi_2.config(text=f"Phi2 Value: {slider_phi_2_value}e-8")
        self.label_A_2.config(text=f"A2 Value: {slider_A_2_value / 1000}")

        self.ax.clear()
        self.ax.legend()
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Amplitude')
        self.ax.set_title('Manual Fitting Tool')
        self.canvas.draw()

if __name__ == '__main__':
    app = ManualFitTool()
    app.mainloop()
