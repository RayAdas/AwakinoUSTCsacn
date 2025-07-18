import pyvisa
import time

# 创建资源管理器
rm = pyvisa.ResourceManager()

# 列出所有可用设备
print(rm.list_resources())

# 打开设备（替换为你的示波器资源名）
scope = rm.open_resource('USB0::0x1AB1::0x0610::HDO1A251400702::INSTR')  # 替换为实际的设备地址
scope.timeout = 10000

# 查询设备标识
idn = scope.query('*IDN?')
print("Device ID:", idn)

# pos = scope.query(':TIMebase:HREFerence:POSition?')
# print("Horizontal Reference Position:", pos)

# 设置延迟时基偏移为 8μs, 设置主时基档位为 2μs
scope.write(':TIMebase:MAIN:OFFSet 0.000008')
scope.write(':TIMebase:MAIN:SCALe 0.000002')

rate = scope.query(':ACQ:SRATe?')
print("Acquisition Sample Rate:", rate)

scope.write(":WAVeform:SOUR CHAN1")  # 通道源1
scope.write(":WAVeform:MODE RAW")  # 波形读取模式普通
scope.write(":WAVeform:FORMat ASCII")  # 设置数据类型

scope.write(':SINGle')
time.sleep(0.5)
max_points = scope.query(':WAVeform:POINts?')
print("Max Points:", max_points)

scope.write(':WAV:STAR 1')
scope.write(':WAVeform:STOP 10000')

data = scope.query(':WAV:DATA?')

print("Waveform Data:", data)

# 关闭连接
scope.close()
