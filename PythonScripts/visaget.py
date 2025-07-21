import pyvisa
import numpy as np
import struct

# 连接示波器
rm = pyvisa.ResourceManager()
scope = rm.open_resource('USB0::0x1AB1::0x0610::HDO1A251400702::INSTR')  # 替换为你的 VISA 地址
scope.timeout = 10000  # 设置超时时间（毫秒）

# 配置波形输出格式
scope.write(":WAV:SOUR CHAN1")       # 选择通道1
scope.write(":WAV:FORM WORD")        # 设置数据格式为BYTE（二进制，常用）
scope.write(":WAV:MODE RAW")        # 标准模式（非平均、非峰值）

# 获取波形参数
x_increment = float(scope.query(":WAV:XINC?"))
x_origin = float(scope.query(":WAV:XOR?"))
y_increment = float(scope.query(":WAV:YINC?"))
y_origin = float(scope.query(":WAV:YOR?"))
y_reference = float(scope.query(":WAV:YREF?"))

# 发送读取数据命令
scope.write(":WAV:DATA?")
raw_data = scope.read_raw()

# 解析数据，跳过示波器的 header
# VISA协议通常数据格式：#<N><NNNNN><data>
if raw_data[0:1] == b'#':
    N = int(raw_data[1:2])
    data_length = int(raw_data[2:2+N])
    data = raw_data[2+N:2+N+data_length]
else:
    raise ValueError("Invalid data format")

# 将二进制数据转为 numpy 数组
data = np.frombuffer(data, dtype=np.uint16)

# 转换为电压值
voltages = (data - y_reference) * y_increment + y_origin

# 生成时间轴
time = np.arange(len(voltages)) * x_increment + x_origin

# 可视化（可选）
import matplotlib.pyplot as plt
plt.plot(time, voltages)
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title("Oscilloscope Waveform")
plt.show()
