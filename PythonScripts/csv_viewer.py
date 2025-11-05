"""
简单的CSV查看工具
用于查看Input目录下的UT C-Scan数据文件
"""

import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, scrolledtext
import os

class CScanViewer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.metadata = {}
        self.data = None
        self.load_data()
        
    def load_data(self):
        """加载CSV文件"""
        print(f"正在加载文件: {self.filepath}")
        
        # 读取元数据（前47行）
        with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
            # 解析元数据
            for i, line in enumerate(lines[:47]):
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    self.metadata[key.strip()] = value.strip()
                elif line.startswith('_'):
                    self.metadata[f'Section_{i}'] = line
                    
        # 读取数据部分（从第47行开始）
        print("正在解析数据...")
        data_lines = []
        with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if i >= 47:  # 跳过前47行header
                    parts = line.strip().split()
                    if len(parts) > 2:  # 确保有数据
                        data_lines.append(parts)
                        
        # 转换为numpy数组
        if data_lines:
            # 第一列是index，第二列是scanning number，其余是waveform data
            self.index = []
            self.scan_num = []
            self.waveforms = []
            
            for parts in data_lines:
                try:
                    self.index.append(int(parts[0]))
                    self.scan_num.append(int(parts[1]))
                    waveform = [float(x) for x in parts[2:]]
                    self.waveforms.append(waveform)
                except ValueError:
                    continue
                    
            self.index = np.array(self.index)
            self.scan_num = np.array(self.scan_num)
            self.waveforms = np.array(self.waveforms)
            
            print(f"数据加载完成! 数据形状: {self.waveforms.shape}")
            print(f"Index范围: {self.index.min()} - {self.index.max()}")
            print(f"Scan范围: {self.scan_num.min()} - {self.scan_num.max()}")
            
    def show_gui(self):
        """显示图形界面"""
        matplotlib.rc("font",family='MicroSoft YaHei',weight="bold")
        root = tk.Tk()
        root.title(f"CSV查看器 - {os.path.basename(self.filepath)}")
        root.geometry("1200x800")
        
        # 创建主框架
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧：元数据显示
        left_frame = ttk.LabelFrame(main_frame, text="文件信息", width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        
        # 元数据文本框
        meta_text = scrolledtext.ScrolledText(left_frame, width=40, height=20)
        meta_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 显示元数据
        for key, value in self.metadata.items():
            if not key.startswith('Section_'):
                meta_text.insert(tk.END, f"{key}: {value}\n")
        meta_text.config(state=tk.DISABLED)
        
        # 数据信息
        info_frame = ttk.LabelFrame(left_frame, text="数据信息")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(info_frame, text=f"数据点数: {len(self.index)}").pack(anchor=tk.W, padx=5)
        ttk.Label(info_frame, text=f"波形长度: {self.waveforms.shape[1]}").pack(anchor=tk.W, padx=5)
        ttk.Label(info_frame, text=f"Index范围: {self.index.min()}-{self.index.max()}").pack(anchor=tk.W, padx=5)
        ttk.Label(info_frame, text=f"Scan范围: {self.scan_num.min()}-{self.scan_num.max()}").pack(anchor=tk.W, padx=5)
        
        # 右侧：图形显示区域
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建notebook用于多标签页
        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 标签页1: C-Scan图像
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="C-Scan图像")
        
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        
        # 重构C-Scan数据为2D矩阵
        max_index = int(self.index.max()) + 1
        max_scan = int(self.scan_num.max()) + 1
        
        # 使用最大值或其他特征值创建C-Scan图像
        cscan_image = np.zeros((max_index, max_scan))
        for i, (idx, scan) in enumerate(zip(self.index, self.scan_num)):
            cscan_image[int(idx), int(scan)] = np.max(np.abs(self.waveforms[i]))
            
        im1 = ax1.imshow(cscan_image.T, aspect='auto', cmap='hot', origin='lower')
        ax1.set_xlabel('Index')
        ax1.set_ylabel('Scan Number')
        ax1.set_title('C-Scan 图像 (最大振幅)')
        plt.colorbar(im1, ax=ax1, label='振幅')
        
        canvas1 = FigureCanvasTkAgg(fig1, tab1)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 标签页2: 示例波形
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="示例波形")
        
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        
        # 显示前几个波形
        sample_rate = float(self.metadata.get('Waveform Sampling Rate(MHz)', '50').split()[0])
        time_axis = np.arange(self.waveforms.shape[1]) / sample_rate  # 微秒
        
        for i in range(min(5, len(self.waveforms))):
            ax2.plot(time_axis, self.waveforms[i+5000], label=f'Index={self.index[i]}, Scan={self.scan_num[i]}', alpha=0.7)
            
        ax2.set_xlabel('时间 (μs)')
        ax2.set_ylabel('振幅')
        ax2.set_title('示例波形')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        canvas2 = FigureCanvasTkAgg(fig2, tab2)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 标签页3: 统计信息
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="统计信息")
        
        fig3, axes3 = plt.subplots(2, 2, figsize=(8, 6))
        
        # 最大振幅分布
        max_amps = np.max(np.abs(self.waveforms), axis=1)
        axes3[0, 0].hist(max_amps, bins=50, edgecolor='black')
        axes3[0, 0].set_xlabel('最大振幅')
        axes3[0, 0].set_ylabel('频数')
        axes3[0, 0].set_title('最大振幅分布')
        
        # 平均振幅分布
        mean_amps = np.mean(np.abs(self.waveforms), axis=1)
        axes3[0, 1].hist(mean_amps, bins=50, edgecolor='black', color='orange')
        axes3[0, 1].set_xlabel('平均振幅')
        axes3[0, 1].set_ylabel('频数')
        axes3[0, 1].set_title('平均振幅分布')
        
        # 波形RMS
        rms_values = np.sqrt(np.mean(self.waveforms**2, axis=1))
        axes3[1, 0].hist(rms_values, bins=50, edgecolor='black', color='green')
        axes3[1, 0].set_xlabel('RMS值')
        axes3[1, 0].set_ylabel('频数')
        axes3[1, 0].set_title('RMS分布')
        
        # 平均波形
        mean_waveform = np.mean(self.waveforms, axis=0)
        axes3[1, 1].plot(time_axis, mean_waveform, 'b-', linewidth=2)
        axes3[1, 1].set_xlabel('时间 (μs)')
        axes3[1, 1].set_ylabel('振幅')
        axes3[1, 1].set_title('平均波形')
        axes3[1, 1].grid(True, alpha=0.3)
        
        fig3.tight_layout()
        
        canvas3 = FigureCanvasTkAgg(fig3, tab3)
        canvas3.draw()
        canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        root.mainloop()


def main():
    """主函数"""
    # 文件路径
    filepath = r"c:\Users\Awaki\Desktop\shit_monitor\Input\BL-H-15J-1.csv"
    
    if not os.path.exists(filepath):
        print(f"错误: 文件不存在 - {filepath}")
        return
        
    # 创建查看器并显示
    viewer = CScanViewer(filepath)
    viewer.show_gui()


if __name__ == "__main__":
    main()
