import tkinter as tk
from tkinter import filedialog
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # 新增导入
import EchoModel

# 打开文件选择对话框
root = tk.Tk()
root.withdraw()  # 不显示主窗口
file_path = filedialog.askopenfilename(
    title="选择npz文件",
    filetypes=[("NPZ files", "*.npz")]
)

if file_path:
    npz = np.load(file_path)
    
else:
    print('未选择文件')

class WaveformViewer:
    def __init__(self, master, npz):
        self.master = master
        self.npz = npz
        if 'data' in npz:
            self.data_x = npz['data'][:, 0]
            self.data_ys = npz['data'][:, 1:]
        else:
            print('该npz文件不包含data字段')
            return
        self.num_curves = self.data_ys.shape[1]
        self.active = [False] * self.num_curves
        self.global_min = np.min(self.data_ys)
        self.global_max = np.max(self.data_ys)

        # 主frame，分为上中下
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=1)
        self.bottom_frame = tk.Frame(self.master)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 上部主区，三列
        self.top_frame = tk.Frame(self.main_frame)
        self.top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.left_param_frame = tk.Frame(self.top_frame)
        self.left_param_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.center_frame = tk.Frame(self.top_frame)
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.right_param_frame = tk.Frame(self.top_frame)
        self.right_param_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # tau滑动条单独行
        self.left_tau_frame = tk.Frame(self.main_frame)
        self.left_tau_frame.pack(side=tk.TOP, fill=tk.X)
        self.right_tau_frame = tk.Frame(self.main_frame)
        self.right_tau_frame.pack(side=tk.TOP, fill=tk.X)

        # Matplotlib图表
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.ax.set_title("Waveform")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Value")
        self.ax.set_xlim(self.data_x.min(), self.data_x.max())
        self.ax.set_ylim(self.global_min, self.global_max)
        self.lines = []
        for i in range(self.num_curves):
            line, = self.ax.plot([], [], lw=2, label=f"Curve {i}")
            self.lines.append(line)
        self.echo_sum_line = self.ax.plot([], [], lw=2, color='purple', label='EchoSum')[0]
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.center_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # EchoModel参数名
        self.param_names = ['fc', 'tau', 'phi', 'alpha', 'beta', 'r', 'tanh_m']
        self.param_defaults = list(EchoModel.echo_info_default)
        self.param_mins = list(EchoModel.echo_info_min)
        self.param_maxs = list(EchoModel.echo_info_max)
        self.left_vars = []
        self.right_vars = []
        self.left_scales = []
        self.right_scales = []
        # 左侧六个滑动条
        for i, name in enumerate(self.param_names):
            if name == 'tau':
                continue
            tk.Label(self.left_param_frame, text=name).pack()
            var = tk.DoubleVar(value=self.param_defaults[i])
            res = (self.param_maxs[i] - self.param_mins[i]) / 1000 if self.param_maxs[i] != self.param_mins[i] else 0.01
            scale = tk.Scale(self.left_param_frame, variable=var, from_=self.param_mins[i], to=self.param_maxs[i],
                             orient=tk.VERTICAL, resolution=res, length=180)
            scale.pack(pady=2)
            var.trace_add('write', lambda *args: self.update_echo_sum_curve())
            self.left_vars.append(var)
            self.left_scales.append(scale)
        # 右侧六个滑动条
        for i, name in enumerate(self.param_names):
            if name == 'tau':
                continue
            tk.Label(self.right_param_frame, text=name).pack()
            var = tk.DoubleVar(value=self.param_defaults[i])
            res = (self.param_maxs[i] - self.param_mins[i]) / 1000 if self.param_maxs[i] != self.param_mins[i] else 0.01
            scale = tk.Scale(self.right_param_frame, variable=var, from_=self.param_mins[i], to=self.param_maxs[i],
                             orient=tk.VERTICAL, resolution=res, length=180)
            scale.pack(pady=2)
            var.trace_add('write', lambda *args: self.update_echo_sum_curve())
            self.right_vars.append(var)
            self.right_scales.append(scale)
        # 左tau滑动条
        tau_idx = self.param_names.index('tau')
        tk.Label(self.left_tau_frame, text='左tau').pack(side=tk.LEFT)
        self.left_tau_var = tk.DoubleVar(value=self.param_defaults[tau_idx])
        tau_res = (self.param_maxs[tau_idx] - self.param_mins[tau_idx]) / 5000
        self.left_tau_scale = tk.Scale(self.left_tau_frame, variable=self.left_tau_var, from_=self.param_mins[tau_idx], to=self.param_maxs[tau_idx],
                                       orient=tk.HORIZONTAL, resolution=tau_res, length=700)
        self.left_tau_scale.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.left_tau_var.trace_add('write', lambda *args: self.update_echo_sum_curve())
        # 右tau滑动条
        tk.Label(self.right_tau_frame, text='右tau').pack(side=tk.LEFT)
        self.right_tau_var = tk.DoubleVar(value=self.param_defaults[tau_idx])
        self.right_tau_scale = tk.Scale(self.right_tau_frame, variable=self.right_tau_var, from_=self.param_mins[tau_idx], to=self.param_maxs[tau_idx],
                                        orient=tk.HORIZONTAL, resolution=tau_res, length=700)
        self.right_tau_scale.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.right_tau_var.trace_add('write', lambda *args: self.update_echo_sum_curve())

        # 按钮区域移到最下方
        self.button_frame = tk.Frame(self.bottom_frame)
        self.button_frame.pack(side=tk.BOTTOM, pady=10)
        self.buttons = []
        for i in range(self.num_curves):
            btn = tk.Button(self.button_frame, text=f"Curve {i}", relief=tk.RAISED,
                            command=lambda idx=i: self.toggle_curve(idx))
            btn.pack(side=tk.LEFT, padx=5)
            self.buttons.append(btn)

        self.update_plot()
        self.update_echo_sum_curve()

    def update_plot(self):
        for i, line in enumerate(self.lines):
            if self.active[i]:
                line.set_data(self.data_x, self.data_ys[:, i])
            else:
                line.set_data([], [])
        # Echo曲线已在update_echo_sum_curve中更新
        legend_labels = [f"Curve {i}" for i, act in enumerate(self.active) if act]
        if self.echo_sum_line.get_xdata().size:
            legend_labels += ["EchoSum"]
        self.ax.legend(legend_labels, loc='upper right')
        self.canvas.draw()

    def toggle_curve(self, idx):
        self.active[idx] = not self.active[idx]
        if self.active[idx]:
            self.buttons[idx].config(relief=tk.SUNKEN, bg="lightblue")
        else:
            self.buttons[idx].config(relief=tk.RAISED, bg="SystemButtonFace")
        self.update_plot()

    def update_echo_sum_curve(self):
        try:
            # 左右参数
            tau_idx = self.param_names.index('tau')
            params_left = []
            params_right = []
            l = 0
            for i, name in enumerate(self.param_names):
                if name == 'tau':
                    params_left.append(self.left_tau_var.get())
                else:
                    params_left.append(self.left_vars[l].get())
                    l += 1
            r = 0
            for i, name in enumerate(self.param_names):
                if name == 'tau':
                    params_right.append(self.right_tau_var.get())
                else:
                    params_right.append(self.right_vars[r].get())
                    r += 1
            t = self.data_x
            y1 = EchoModel.echo_function(t, params_left[1], params_left[4], fc=params_left[0], phi=params_left[2], alpha=params_left[3], r=params_left[5], tanh_m=params_left[6])
            y2 = EchoModel.echo_function(t, params_right[1], params_right[4], fc=params_right[0], phi=params_right[2], alpha=params_right[3], r=params_right[5], tanh_m=params_right[6])
            y_sum = y1 + y2
            self.echo_sum_line.set_data(t, y_sum)
        except Exception as e:
            self.echo_sum_line.set_data([], [])
        self.update_plot()

# 创建Tkinter主窗口
root.deiconify()
root.title("Waveform Viewer")
root.geometry("1000x600")

viewer = WaveformViewer(root, npz)
root.mainloop()
