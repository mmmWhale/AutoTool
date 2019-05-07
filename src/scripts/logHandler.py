import threading
import time
import sys
import os
import src.scripts.serialConnect


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
                if src.scripts.serialConnect.ser.is_open:

                    # 读取一行数据
                    line_byte_txt = src.scripts.serialConnect.ser.readline()

                    # 判断数据是否为空
                    if len(line_byte_txt) != 0 and  src.scripts.serialConnect.ser.inWaiting() != 0:
                        # 将读取的数据转化为字符串并在控制台打印，保存至log.txt中
                        line_str_txt = str(line_byte_txt, encoding="utf-8")
                        print(time.strftime("[%Y%m%d_%H:%M:%S]", time.localtime()) + line_str_txt, file=logfile_a)
                        src.scripts.serialConnect.ser.flush()
                        sys.stdout.flush()
                    else:
                        time.sleep(0.05)
                else:
                    print("串口未连接成功,中断退出......")
                    src.scripts.serialConnect.ser.close()
                    os._exit(0)



# log分析器
# keycode:事件触发的关键字
# stopflag:判断此次事件已经执行完成的关键字，防止未匹配到触发关键字
# cycletime=120：默认120s未检测到关键字则停止此次关键字匹配分析，防止阻塞其他命令的执行判断
def log_scanner(keyword, stopflag, cycletime=120):

    # 判断日志文件是否存在
    if os.path.isfile("log.txt"):
        with open("log.txt", "r", encoding="utf-8") as logfile_r:
            # 把指针移至文件末尾
            logfile_r.seek(0,2)

            while True:
                line_txt = logfile_r.readline()
                # 判断是否有新增内容，没有则等待50ms
                if not line_txt.strip():
                    time.sleep(0.05)
                    continue
                else:
                    yield line_txt
                    # 判断关键字是否存在
                    if keyword in line_txt:
                        logfile_r.seek(0, 2)
                        return True
                    elif stopflag in line_txt:
                        break
                    else:
                        return False

