import pyvisa

# 创建资源管理器
rm = pyvisa.ResourceManager()

# 列出所有可用设备
print(rm.list_resources())

# 打开设备（替换为你的示波器资源名）
scope = rm.open_resource('USB0::0x1AB1::0x0610::HDO1A251400702::INSTR')  # 替换为实际的设备地址

# 发送 SCPI 指令，例如清除指令 *CLS
scope.write(':CLEar')

# 查询设备标识
idn = scope.query('*IDN?')
print("Device ID:", idn)

# 关闭连接
scope.close()
