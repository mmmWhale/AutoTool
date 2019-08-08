#!/usr/bin/env python3
import threading
import time
import sys
import os
import serial.tools.list_ports
import re


class LogThread(threading.Thread):

    # 覆写线程run方法
    def run(self):
        print("开始线程：" + self.name)

        # 追写方式打开日志文件
        # 如果log.txt在同目录下不存在，则自动创建
        # 如果已存在log.txt文件，则往文件里追加内容，不会覆盖
        with open("log.txt", "a", encoding='utf-8') as logfile_a:
            # 循环读取数据
            while True:
                # 判断串口是否连接成功
                if ser.is_open:

                    # 读取一行数据
                    line_byte_txt = ser.readline()

                    # 判断数据是否为空
                    if len(line_byte_txt) != 0 and  ser.inWaiting() != 0:
                        # 将读取的数据转化为字符串并在控制台打印，保存至log.txt中
                        line_str_txt = time.strftime("[%Y%m%d_%H:%M:%S]", time.localtime())+str(line_byte_txt, encoding="utf-8")
                        #去除某个智障在log字符串加的颜色相关字符
                        line_str_txt = re.sub(r"\x1B\[([0-9]{1,2}(;[0-9]{1,2})*)?m","",line_str_txt)
                        print(line_str_txt.replace("\0","").replace("\r","").replace("\n",""),file=logfile_a)

                        #写入一次保存一次
                        logfile_a.flush()
                        #sys.stdout.flush()
                    else:
                        time.sleep(0.05)
                else:
                    print("串口未连接成功,中断退出......")
                    ser.close()
                    os._exit(0)




# log分析器
# keyword:事件触发的关键字
# stopflag:判断此次事件已经执行完成的关键字，防止未匹配到触发关键字
# cycletime=120：默认120s未检测到关键字则停止此次关键字匹配分析，防止阻塞其他命令的执行判断
def logscanner(keyword,stopflag,cycletime=120):

    # 判断日志文件是否存在
    if os.path.isfile("log.txt"):
        with open("log.txt", "r", encoding="utf-8") as logfile_read:
            # 把指针移至文件末尾
            logfile_read.seek(0,2)
            start_time=time.perf_counter()
            
            while True:
                line_txt = logfile_read.readline()
                # 判断是否有新增内容，没有则等待50ms
                if not line_txt.strip():
                    time.sleep(0.05)
                    continue
                else:
                    #yield line_txt
                    print (line_txt)
                    # 判断关键字是否存在
                    if keyword in line_txt:
                        logfile_read.seek(0, 2)
                    elif stopflag in line_txt:
                        return 1
                    elif time.perf_counter()-start_time>120:
                        return 2
    else:
        print ("日志文件不存在")
        return 0



def runCMD(cmd):
    ser.write(b'root\r')
    ser.write(cmd)





if __name__=="__main__":

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
            print ("串口连接成功")
            thread_log=LogThread()
            
            #设置为守护线程，防止ctrl+c没有退出的情况
            thread_log.setDaemon("True")
            thread_log.start()
            time.sleep(1)

             #_thread.start_new_thread(函数名,(函数参数,))

        except serial.serialutil.SerialException:
            print("串口已经被连接，请检测其他软件")

    elif num >= 2:
        print("检测到多个串口连接，请断开其他设备串口后重新运行")
    else:
        print("未检测到设备串口，请检查后重新运行 :)")


