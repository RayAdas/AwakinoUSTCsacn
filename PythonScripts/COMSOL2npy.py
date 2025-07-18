import numpy as np
import tkinter as tk
from tkinter import filedialog
import re  # 新增导入

def txt_to_npz(txt_path, npz_path):
    data = []
    metadata = {}
    time_unit = None  # 新增：记录时间单位

    with open(txt_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('%'):
                if ':' in line:
                    # 提取元数据，例如：% Model: USShiftingSim.mph
                    key, value = line[1:].split(':', 1)
                    metadata[key.strip()] = value.strip()
                # 新增：正则匹配“时间 (单位)”
                match = re.search(r'时间\s*\((\w+)\)', line)
                if match:
                    time_unit = match.group(1).lower()
            elif line:
                values = [float(x) for x in line.split(',')]
                data.append(values)

    array = np.array(data)

    # 新增：根据time_unit转换首列为秒
    if time_unit:
        unit_map = {
            's': 1,
            'ms': 1e-3,
            'µs': 1e-6,
            'ns': 1e-9,
            'ps': 1e-12,
            'min': 60,
            'h': 3600
        }
        factor = unit_map.get(time_unit, 1)
        array[:, 0] = array[:, 0] * factor

    # 保存数据和元数据
    np.savez(npz_path, data=array, metadata=metadata)
    print(f"已保存为 {npz_path}")

# 示例调用
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    txt_path = filedialog.askopenfilename(
        title="选择输入的txt文件",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if txt_path:
        npz_path = txt_path.rsplit('.', 1)[0] + '.npz'
        txt_to_npz(txt_path, npz_path)
    else:
        print("未选择文件。")