#!usr/bin/env python3
#encoding:utf-8

import re
import linecache


CN_Command_Threshold = -10.65
EN_Command_Threshold = 2.49


list1_wakeup_tmp=[]
list1_command_tmp=[]

list1_wakeup_command=[]
list1_number_command=[]
list1_pure_command=[]

list2_wakeup_command=[]
list2_number_command=[]
list2_pure_command=[]

# 用以储存音频名称
f1_wav_names=[]
f2_wav_names=[]

# 用以储存包含str wav名称的行数
line_number_list=[]

ten_db_reslut_list=[]
five_db_reslut_list=[]
quiet_reslut_list=[]

quiet_reslut=float()
five_db_reslut=float()
ten_db_reslut=float()




with open('f1.txt','r')as f1,open('f2.txt','r')as f2,open('纯命令词识别错误统计.txt','a')as f5,open('纯命令词未识别统计.txt','a')as f6,open('RAM统计.txt','a')as f7:
    # 清洗标注数据，除去快语速，筛选出正常语速唤醒词/纯命令词/闹钟倒计时数字类命令词
    file1_list = linecache.getlines('f1.txt')

#    for i,val in enumerate(file1_list):
#        if val:
#            if i%2==0:
#               list1_wakeup_tmp.append(val)
#           else:
#                list1_command_tmp.append(val)

#    list1_wakeup_command=list1_wakeup_tmp[1::2]
    for j in file1_list:
        if j:
            j_tmp = (j.split('	', 4)[3]).lower().replace(' ', '').strip()
            if j_tmp.find('小爱同学') != -1 or j_tmp.find('alexa') != -1:
                list1_wakeup_command.append(j)
            elif j_tmp.find('闹钟') != -1 or j_tmp.find('倒计时') != -1 or j_tmp.find('alarm') != -1 or j_tmp.find('countdown') != -1:
                if j_tmp.find('打开闹钟') == -1 and j_tmp.find('停止闹钟') == -1 and j_tmp.find('打开倒计时') == -1 and j_tmp.find('openalarm') == -1:
                    list1_number_command.append(j)
                else:
                    list1_pure_command.append(j)
            else:
                list1_pure_command.append(j)
    f1_wav_name_1 = list1_pure_command[0].split('\t', 4)[0].replace('.wav', '')
    globals()['f1_'+f1_wav_name_1] = []
    f1_wav_names.append(f1_wav_name_1)
    for i in list1_pure_command:
        i_wav_name = i.split('\t', 4)[0].replace('.wav', '')
        # print(i_wav_name)
        if i_wav_name not in f1_wav_names:
            f1_wav_names.append(i_wav_name)
            globals()['f1_' + i_wav_name] = []
            globals()['f1_' + i_wav_name].append(i)
        else:
            globals()['f1_' + i_wav_name].append(i)



    # 清洗日志数据，筛选出唤醒词/纯命令词/数字类命令词/RAM打印
    file2_list=linecache.getlines('f2.txt')
    # 判断"str_wav:"出现的行数序号
    for line, file2_list_content in enumerate(file2_list):
        if 'str_wav:' in file2_list_content.strip():
            line_number_list.append(line)

    # 保存
    for i, line_number  in enumerate(line_number_list):
         i_wav_name = file2_list[(line_number_list[i])].replace('str_wav:', '').replace('.en.wav', '').replace('.cn.wav', '').replace('.wav', '').strip()
         f2_wav_names.append(i_wav_name)
         globals()['f2_' + i_wav_name] = []
         list_tmp=[]
         if i < len(line_number_list)-1:
             list_tmp=file2_list[line_number:line_number_list[i+1]:1]
         elif i == len(line_number_list)-1:
             list_tmp=file2_list[line_number::1]

         for k in list_tmp:
             if re.search(r'[-+]?[0-9]{1,6}[.][0-9]*[\s]+[-+]?[0-9]{1,6}[.][0-9]*[\s]+', k, ):
                 k_tmp = k.lower().replace(' ', '').strip()
                 if k_tmp.find('小爱同学') != -1 or k_tmp.find('alexa') != -1:
                    list2_wakeup_command.append(k)
                 elif k_tmp.find('闹钟') != -1 or k_tmp.find('倒计时') != -1 or k_tmp.find('alarm') != -1 or k_tmp.find('countdown') != -1:
                    if k_tmp.find('打开闹钟') == -1 and k_tmp.find('停止闹钟') == -1 and k_tmp.find('打开倒计时') == -1 and k_tmp.find('openalarm') == -1:
                        list2_number_command.append(k)
                    else:
                        globals()['f2_' + i_wav_name].append(k)
                 else:
                     globals()['f2_' + i_wav_name].append(k)
             elif k.replace(' ', '').strip().find('heapremine') != -1:
                 f7.writelines(k.replace('\r', '').replace('\n', '').replace(',', ' ').strip() + '\n')

    #print(f1_wav_names)
    #print(f2_wav_names)
    #print(globals().get('f1_format_huami_rt0.4s_quiet_near_guiyihua_012_guiyihua'))

    for f1_wav_name in f1_wav_names:
        for f2_wav_name in f2_wav_names:
            if f2_wav_name == f1_wav_name:
                wakeup_pass_count = 0
                wakeup_fail_count = 0
                wakeup_missing_count = 0

                pure_command_pass_count = 0
                pure_command_fail_count = 0
                pure_command_missing_count = 0

                # 进行判断，统计纯命令识别率
                for p in globals().get('f1_'+f1_wav_name):
                    data2_list = p.split('	', 4)
                    for q in globals().get('f2_'+f2_wav_name):
                        Q1 = re.findall(r'[-+]?[0-9]{1,4}[.][0-9]*', q)

                        # print(L1)
                        pure_command_stop_time = Q1[1]
                        pure_command_start_time = Q1[0]
                        pure_command_fraction = float(Q1[2].strip())

                        # 英文命令词
                        pure_command_words = ''.join(re.findall(r'(?<=\s)[a-zA-Z]+(?=\s)', q))
                        Command_Threshold = EN_Command_Threshold

                        # 判断使用英文/中文阈值
                        if not pure_command_words:
                            # 中文命令词
                            pure_command_words = ''.join(re.findall(r'[\u4e00-\u9fa5]', q))
                            Command_Threshold = CN_Command_Threshold

                        #print(pure_command_words)
                        if float(pure_command_start_time.strip()) >= (float(data2_list[1]) - 0.3) and float(
                                pure_command_start_time.strip()) < (float(data2_list[2]) + 0.3):
                            # print("日志的命令:"+pure_command_words.lower().replace(' ','').strip())
                            # print("测试集的命令："+str(data2_list[3]).lower().replace(' ','').strip())

                            if (str(data2_list[3]).lower().replace(' ', '').strip()) == pure_command_words.lower().replace(' ', '').strip() :
                                if pure_command_fraction >= Command_Threshold:
                                    pure_command_pass_count = pure_command_pass_count + 1
                                    break
                                elif pure_command_fraction < Command_Threshold:
                                    pure_command_missing_count = pure_command_missing_count + 1
                                    f6.writelines(data2_list[1] + '\t' + data2_list[2] + '\t' + str(data2_list[3]).strip() + '\n')
                                    break
                            else:
                                pure_command_fail_count = pure_command_fail_count + 1
                                f5.writelines(pure_command_start_time + '\t' + pure_command_stop_time + '\t' + str(data2_list[3]).strip() + '\t' + pure_command_words + '\t' + str(pure_command_fraction) + '\n')
                                break
                        else:
                            if globals().get('f2_'+f2_wav_name).index(q) == (len(globals().get('f2_'+f2_wav_name)) - 1):
                                pure_command_missing_count = pure_command_missing_count + 1
                                f6.writelines(data2_list[1] + '\t' + data2_list[2] + '\t' + str(data2_list[3]).strip() + '\n')
                print("<---------------------------------------------------------")
                print(f1_wav_name)
                print('纯命令词识别率为:{:.2%}'.format(pure_command_pass_count / len(globals().get('f1_'+f1_wav_name))))
                print("识别错误次数为:" + str(pure_command_fail_count))
                print("识别成功次数为:" + str(pure_command_pass_count))
                print("未识别出纯命令次数为:" + str(pure_command_missing_count))
                print("测试集共计纯命令词个数:" + str(len(globals().get('f1_'+f1_wav_name))))
                print("测试结果共计纯命令词个数:" + str(len(globals().get('f2_'+f2_wav_name))))
                print("--------------------------------------------------------->")
                if 'snrp10' in f1_wav_name:
                    ten_db_reslut_list.append(pure_command_pass_count / len(globals().get('f1_'+f1_wav_name)))
                elif 'snrp5' in f1_wav_name:
                    five_db_reslut_list.append(pure_command_pass_count / len(globals().get('f1_' + f1_wav_name)))
                else:
                    quiet_reslut_list.append(pure_command_pass_count / len(globals().get('f1_' + f1_wav_name)))
    if five_db_reslut_list:
        for reslut in five_db_reslut_list:
            five_db_reslut += float(reslut)
        print("5db环境下平均结果:{:.2%}".format(five_db_reslut / len(five_db_reslut_list)))
        print("5db环境下共" + str(len(five_db_reslut_list)) + "个测试集")
    if ten_db_reslut_list:
        for reslut in ten_db_reslut_list:
            ten_db_reslut += float(reslut)
        print("10db环境下平均结果:{:.2%}".format(ten_db_reslut / len(ten_db_reslut_list)))
        print("10db环境下共" + str(len(ten_db_reslut_list)) + "个测试集")
    if quiet_reslut_list:
        for reslut in quiet_reslut_list:
            quiet_reslut += float(reslut)
        print("安静环境下平均结果:{:.2%}".format(quiet_reslut / len(quiet_reslut_list)))
        print("安静环境下共" + str(len(quiet_reslut_list)) + "个测试集")




