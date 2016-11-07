#! usr/bin/python
# coding=utf-8

import os
import time
import threading
class Get:
    def __int__(self):
        self.cpu_usage = None
        self.memory_usage = None


    def start(self):
        self.cpu_th = threading.Thread(target=self.thread_getCpu)
        self.cpu_th.setDaemon(True)
        self.cpu_th.start()

    def exeCmd(self, cmd):
        '''根据终端命令获取内容'''
        r = os.popen(cmd)
        text = r.read()
        r.close()
        return text

    def writeFile(self, filename, data):
        '''写入文档'''
        f = open(filename, "w")
        f.write(data)
        f.close()
    def get_sys_run_time(self):
        '''系统运行时间和空闲时间统计'''
        time = self.exeCmd("cat /proc/uptime | awk '{print $1,$2}'").replace('\n','').split(' ')
        run_time = int(float(time[0])/1)
        free_time = time[1]

        D = int(run_time/86400)
        H = int((run_time % 86400)/3600)
        M = int(((run_time % 86400)%3600)/60)
        S = int(((run_time % 86400)%3600)%60)

        alread_run = '系统已经运行：%s天%s时%s分%s秒'%(D,H,M,S)

        #获取cpu个数
        cpu_num = self.exeCmd('cat /proc/cpuinfo| grep "processor"| wc -l')
        #计算空闲时间: 系统的空闲率(%) = num2/(num1*N) 其中N是SMP系统中的CPU个数
        free_usage = float(free_time) / (run_time * int(cpu_num)) *100

        return alread_run, free_usage

    def get_sda(self):
        sda = self.exeCmd("df -h | grep sda | awk '{print $1,$2,$3,$4,$5}'").split('\n')
        sda_list = []
        # print(sda)
        for num in sda:
            if num:
                temp = num.split(' ')
                sda_list.append(temp)
        return sda_list

    def getMemoryUsage(self):
        '''
                total               used        free        shared      buffers     cached
        Mem:    5947280             4467932     1479348     48076       197788      1904676
        - / +   buffers / cache:    2365468     3581812
        Swap:   7811068             0           7811068
        '''
        # 采用第三行的数据计算内存占有率
        Mem_list = self.exeCmd("free -m | sed -n '3p' | awk '{print $3,$4}'").replace('\n', '').split(' ')
        Mem_used = float(Mem_list[0])
        Mem_free = float(Mem_list[1])
        Mem_total = Mem_used+Mem_free
        Mem_usage = float(Mem_used / Mem_total * 100)

        return '%.2f' % Mem_usage,Mem_used,Mem_free,Mem_total

    def get_idel_total(self):
        cpu_list = self.exeCmd("cat /proc/stat | grep 'cpu' | awk '{print $2,$3,$4,$5,$6,$7,$8}'").split('\n')
        cpu_idel = []
        cpu_total = []
        for cpu_item in cpu_list:
            cpu_item = cpu_item.split(' ')
            if len(cpu_item) > 2:
                cpu_idel.append(int(cpu_item[3]))
                total = 0
                for cpu_inf in cpu_item:
                    total += int(cpu_inf)
                cpu_total.append(total)
        return cpu_idel, cpu_total

    def getCpuUsage(self):
        '''获取cpu使用率，一秒间隔'''
        idel_1, total_1 = self.get_idel_total()
        time.sleep(1)
        idel_2, total_2 = self.get_idel_total()
        cpu_usage = []
        for i in range(0, len(idel_1)):
            err_idel = int(idel_2[i]) - int(idel_1[i])
            err_total = int(total_2[i]) - int(total_1[i])
            usage = 100 - (err_idel / err_total * 100)
            cpu_usage.append('%.2f' % usage)
        return cpu_usage

    def thread_getCpu(self):
        while True:
            self.cpu_usage = self.getCpuUsage()

c=Get()
c.get_sda()
#
# c.getMemoryUsage()
    # def thread_getMem(self):
    #     while True:
    #         self.memory_usage = self.getMemoryUsage()




