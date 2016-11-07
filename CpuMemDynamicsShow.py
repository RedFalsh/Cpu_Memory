#! usr/bin/python
# coding=utf-8

import os
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.font_manager as fm
import matplotlib.dates as dates

# 查看字体命令： fc-list :lang=zh
myfont = fm.FontProperties(fname='/usr/share/fonts/truetype/arphic/uming.ttc')

import threading


class Queue:
    def __init__(self):
        self.items = []
        for i in range(0, 60):
            self.items.append(0)

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        return self.items.pop(0)

    def empty(self):
        return self.size() == 0

    def size(self):
        return len(self.items)


class Cpu_Inf(object):
    def __int__(self):
        self.cpu_usage = None
        self.memory_usage = None

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

    def getMemoryUsage(self):
        '''
                total               used        free        shared      buffers     cached
        Mem:    5947280             4467932     1479348     48076       197788      1904676
        - / +   buffers / cache:    2365468     3581812
        Swap:   7811068             0           7811068
        '''
        # 采用第三行的数据计算内存占有率
        Mem_list = self.exeCmd("free | sed -n '3p' | awk '{print $3,$4}'").replace('\n', '').split(' ')
        Mem_used = float(Mem_list[0])
        Mem_free = float(Mem_list[1])
        Mem_usage = int(Mem_used / (Mem_used + Mem_free) * 100)

        return '%.2f' % Mem_usage

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

    def getCpu(self):
        while True:
            self.cpu_usage = self.getCpuUsage()
            self.memory_usage = self.getMemoryUsage()


###############################################################
#                         曲线                                #
###############################################################
class Matplot():
    def __init__(self):
        self.cpu = Cpu_Inf()

    def start2(self):
        cpu_th = threading.Thread(target=self.cpu.getCpu)
        cpu_th.setDaemon(True)
        cpu_th.start()

        # First set up the figure, the axis, and the plot element we want to animate
        # self.fig = plt.subplot(111)
        self.fig = plt.figure()

        self.ax_cpu = self.fig.add_subplot(2, 1, 1, xlim=(0, 60), ylim=(0, 100))
        self.line_cpu, = self.ax_cpu.plot([], [], label='cpu', color='blue', linewidth=2.5, linestyle="-")
        plt.grid()
        plt.legend()
        plt.ylabel("CPU利用率（%）", fontproperties=myfont)

        self.ax_mem = self.fig.add_subplot(2, 1, 2, xlim=(0, 60), ylim=(0, 100))
        self.line_mem, = self.ax_mem.plot([], [], label='mem', color='red', linewidth=2.5, linestyle="-")
        plt.grid()
        plt.legend()
        plt.xlabel("时间（s）", fontproperties=myfont)
        plt.ylabel("内存利用率（%）", fontproperties=myfont)

        time.sleep(1.5)

        self.que_cpu = Queue()
        self.que_mem = Queue()

        anim = animation.FuncAnimation(self.fig, self.animate, init_func=self.init,
                                       frames=200, interval=1000, blit=True)

        plt.show()

    def init(self):
        self.line_cpu.set_data([], [])
        self.line_mem.set_data([], [])
        return self.line_cpu,self.line_mem,

    def get_x_y(self, que, cpu_usage):
        x = np.linspace(1, 60, 60)
        que.enqueue(cpu_usage)  # 入队
        que.dequeue()  # 出队
        y = que.items
        return x, y

    def animate(self, i):
        x, y = self.get_x_y(self.que_cpu, self.cpu.cpu_usage[0])
        self.line_cpu.set_data(x, y)
        x, y = self.get_x_y(self.que_mem, self.cpu.memory_usage)
        self.line_mem.set_data(x, y)

        return self.line_cpu,self.line_mem,

a = Matplot()
a.start2()


