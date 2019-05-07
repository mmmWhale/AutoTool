import serial
import serial.tools.list_ports


# 获取所有的串口ListPortInfo对象，存入List列表内
port_list = list(serial.tools.list_ports.comports())
# 记录电脑所连接串口的数量
num = len(port_list)
# 用以记录List列表内特定ListPortInfo对象的下标
flag = 0

# 遍历所有的ListPortInfo对象
for i,port in enumerate(port_list):
    # 目前大部分测试设备连接串口的manufacturer都是Silicon Laboratories
    # 通过判断串口，来保障连接的是测试设备
    if port.manufacturer == "(标准端口类型)":
        num = num -1
    else:
        flag = i


# 只有一台设备连接的情况
if num == 1:
    try:
        # 连接测试设备串口 设置端口号 波特率 数据位 停止位
        ser = serial.Serial(port_list[flag].device, baudrate=115200, bytesize=8, stopbits=1, timeout=2)
    except serial.serialutil.SerialException:
        print("串口已经被连接，请检测其他软件")
    else:
        print("串口连接失败")

elif num >= 2:
    print("检测到多个串口连接，请断开其他设备串口后重新运行")
else:
    print("未检测到设备串口，请检查后重新运行 :)")


