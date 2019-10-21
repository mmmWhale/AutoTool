#!/usr/bin/env python3
import threading
import time
import sys
import os
import serial.tools.list_ports
import re
import _thread
import winsound
from datetime import datetime



class LogThread(threading.Thread):

    def __init__(self,ser,com_name):
        threading.Thread.__init__(self)
        self.ser = ser
        self.com_name = str(com_name)      

    # 覆写线程run方法
    def run(self):      
        #print("开始线程：" + self.name)

        # 是否需要添加时间戳的标志
        split_flag_time=True
        # 是否需要换行的标志
        split_flag_wrap_1=True
        
        # 追写方式打开日志文件
        # 如果log.txt在同目录下不存在，则自动创建
        # 如果已存在log.txt文件，则往文件里追加内容，不会覆盖
        with open("log_"+self.com_name+".txt", "ab",buffering=0) as logfile_a:
            
            # 判断串口是否连接成功
            if self.ser.is_open:
                print(self.com_name+"已连接")
                # 循环读取数据
                while True:
                    buffer_bytes=self.ser.inWaiting()
                    # 判断数据是否为空                                       
                    if buffer_bytes:
                        #print(buffer_bytes)
                        # 读取缓存中所有字节，转化为字符串进行处理                        
                        line_byte_txt=self.ser.read(buffer_bytes)                       
                        line_str_txt = str(line_byte_txt,encoding="utf-8",errors="ignore")                                                  
                        #line_str_txt = re.sub(r"\x1B\[([0-9]{1,2}(;[0-9]{1,2})*)?m","", line_str_txt)
                        # 去除单个的\r或\n情况，只保留\r\n组合
                        line_str_txt_list=re.split(r"\r\n",re.sub(r"(\r(?!\n))|((?<!\r)\n)","",line_str_txt))
                        
                        # 计算分割后列表长度                         
                        len_line_str_txt_list=len(line_str_txt_list)
                        
                        #print("******"+line_str_txt_list[len_line_str_txt_list-1])
                        
                        # 判断分割后的列表，是否有字符串残留，以判断写入时是否需要换行
                        if line_str_txt_list[len_line_str_txt_list-1]:
                            split_flag_wrap_1=False                                                                                                           
                        else:
                            split_flag_wrap_1=True 
                        
                                            
                        for i in range(len_line_str_txt_list):                           
                            if len_line_str_txt_list==1:
                                split_flag_wrap=False
                            elif len_line_str_txt_list>1:
                                # 是否添加时间戳由上游标志决定，但必须换行（因为第一个元素后面必定有\r\n）
                                if i==0:
                                    split_flag_wrap=True 
                                # 必须添加时间戳和换行（完整的一行）    
                                elif i>0 and i<len_line_str_txt_list-1:
                                    split_flag_time=True
                                    split_flag_wrap=True
                                # 必须添加时间戳，是否换行，得看本次分割后列表最后一个是空串还是需要衔接下一轮的字符串    
                                elif i==len_line_str_txt_list-1:
                                    split_flag_time=True
                                    split_flag_wrap=split_flag_wrap_1
                            
                            if line_str_txt_list[i]:
                                # 下轮读出的字节不需要时间戳的情况
                                if split_flag_time:
                                    # 判断本次是否需要添加换行符                                
                                    if split_flag_wrap:                            
                                        logfile_a.write(bytes("["+datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]+"]"+re.sub(r"\x1B\[([0-9]{1,2}(;[0-9]{1,2})*)?m","", line_str_txt_list[i])+"\n",encoding="utf-8",errors="ignore"))                                                                                
                                    else:
                                        logfile_a.write(bytes("["+datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]+"]"+re.sub(r"\x1B\[([0-9]{1,2}(;[0-9]{1,2})*)?m","", line_str_txt_list[i]),encoding="utf-8",errors="ignore"))                                                                                                                     
                                        # 标记下一轮读出的字节需要不添加时间戳，但需要换行的情况
                                        split_flag_time=False                                                                                                             
                                else:                                   
                                    # 判断本次是否需要添加换行符                                
                                    if split_flag_wrap:                                       
                                        #不需要添加时间戳，但需要换行,完成了拼凑的情况
                                        logfile_a.write(bytes(re.sub(r"\x1B\[([0-9]{1,2}(;[0-9]{1,2})*)?m","", line_str_txt_list[i])+"\n",encoding="utf-8",errors="ignore"))
                                        split_flag_time=True                                                                               
                                    else:
                                        logfile_a.write(bytes(re.sub(r"\x1B\[([0-9]{1,2}(;[0-9]{1,2})*)?m","", line_str_txt_list[i]),encoding="utf-8",errors="ignore"))                                                                    

                            # 写入一次保存一次
                            logfile_a.flush()
                            sys.stdout.flush()
                    else:          
                        time.sleep(0.1)
            else:
                print("串口未连接成功,中断退出......")
                self.ser.close()
                os._exit(0)


# log分析器
# keyword:事件触发的关键字
# stopflag:判断此次事件已经执行完成的关键字，防止未匹配到触发关键字
# cycletime=120：默认120s未检测到关键字则停止此次关键字匹配分析，防止阻塞其他命令的执行判断
def logscanner(keyword,stopflag, cycletime=120):
    # 判断日志文件是否存在
    if os.path.isfile("log.txt"):
        with open("log.txt", "r", encoding="utf-8") as logfile_read:
            # 把指针移至文件末尾
            logfile_read.seek(0, 2)
            start_time = time.perf_counter()

            while time.perf_counter() - start_time < cycletime:
                line_txt = logfile_read.readline()
                # 判断是否有新增内容，没有则等待50ms
                if not line_txt.strip():
                    time.sleep(0.05)
                    continue
                else:
                    # yield line_txt
                    # print ("打印："+line_txt)
                    # 判断关键字是否存在

                    if keyword in line_txt:
                        logfile_read.seek(0, 2)
                    elif stopflag in line_txt:
                        return 1

            return 2
    else:
        print ("日志文件不存在")
        return 0


def runCMD(cmd):
    ser.write(b'root\r')
    ser.write(cmd)


if __name__ == "__main__":     
    # 获取所有的串口ListPortInfo对象，存入List列表内
    all_port_list = list(serial.tools.list_ports.comports())
    # 记录电脑所连接串口的数量
    num = len(all_port_list)
    # 用以记录List列表内特定ListPortInfo对象的下标
    #flag = 0

    # 遍历所有的ListPortInfo对象
    for i,port in enumerate(all_port_list):
    # 目前大部分测试设备连接串口的manufacturer都是Silicon Laboratories
    # 通过判断串口，来保障连接的是测试设备
        if port.manufacturer == "(标准端口类型)":
            num = num -1
            all_port_list.remove(all_port_list[i])        
       

    # 只有一台设备连接的情况
    if num >= 0:
        try:
            for listPortInfo in all_port_list:
                # 连接测试设备串口 设置端口号 波特率 数据位 停止位
                ser = serial.Serial(listPortInfo.device, baudrate=115200, bytesize=8, stopbits=1, timeout=2)
                #print ("串口连接成功")
                #设置为守护线程，防止ctrl+c没有退出的情况
                logThread=LogThread(ser,listPortInfo.device)
                logThread.setDaemon("True")
                logThread.start()                
                time.sleep(1)
            while True:
                pass
             #_thread.start_new_thread(函数名,(函数参数,))

        except serial.serialutil.SerialException:
            print("串口已经被连接，请检测其他软件")

    else:
        print("未检测到设备串口，请检查后重新运行 :)")
    input()




