#! usr/bin/python
#coding=utf-8

import os
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.font_manager as fm
#查看字体命令： fc-list :lang=zh
myfont = fm.FontProperties(fname='/usr/share/fonts/truetype/arphic/uming.ttc')

import threading


class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        return self.items.pop(0)

    def empty(self):
        return self.size() == 0

    def size(self):
        return len(self.items)
class cpu_state_class(object):
    def __int__(self):
        self.cpu_usage_list = None

    def exeCmd(self,cmd):
        r = os.popen(cmd)
        text = r.read()
        r.close()
        return text

    def writeFile(self,filename,data):
        f = open(filename,"w")
        f.write(data)
        f.close()

    def getMemoryUsage(self):
        '''
                total               used        free        shared      buffers     cached
        Mem:    5947280             4467932     1479348     48076       197788      1904676
        - / +   buffers / cache:    2365468     3581812
        Swap:   7811068             0           7811068
        '''
        #采用第三行的数据计算内存占有率
        Mem_list = self.exeCmd("free | sed -n '3p' | awk '{print $3,$4}'").replace('\n', '').split(' ')
        Mem_used = float(Mem_list[0])
        Mem_free = float(Mem_list[1])
        Mem_usage = int(Mem_used/(Mem_used + Mem_free)*100)

        return ("内存占有率："+'%d'%Mem_usage + '%')

    def cpu_usage(self):
        cpu_list = self.exeCmd("cat /proc/stat | grep 'cpu ' | awk '{print $2,$3,$4,$5,$6,$7,$8}'").replace('\n','').split(' ')
        idel_1 = cpu_list[3]
        total_1=0
        for cpu in cpu_list:
            total_1 += int(cpu)
        time.sleep(1)
        cpu_list = self.exeCmd("cat /proc/stat | grep 'cpu ' | awk '{print $2,$3,$4,$5,$6,$7,$8}'").replace('\n', '').split(' ')
        idel_2 = cpu_list[3]
        total_2 = 0
        for cpu in cpu_list:
            total_2 += int(cpu)

        err_idel = int(idel_2) - int(idel_1)
        err_total = int(total_2) - int(total_1)

        cpu_usage = 100-(err_idel/err_total*100)

        print('%.3f'%(cpu_usage/1)+'%')
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
        return cpu_idel,cpu_total

    def cpu_usage1(self):
        while True:
            idel_1,total_1 = self.get_idel_total()
            time.sleep(1)
            idel_2, total_2 = self.get_idel_total()
            cpu_usage = []
            for i in range(0,len(idel_1)):
                err_idel = int(idel_2[i]) - int(idel_1[i])
                err_total = int(total_2[i]) - int(total_1[i])
                usage = 100-(err_idel/err_total*100)
                cpu_usage.append('%.2f'%usage)
            self.cpu_usage_list = cpu_usage
            # print(cpu_usage)
            # return cpu_usage

###############################################################
#                         曲线                                 #
###############################################################
    def init(self):
        self.line.set_data([], [])
        self.line1.set_data([], [])
        return self.line,self.line1

    def get_x_y(self, que, cpu_usage):
        x = np.linspace(1, 60, 60)
        que.enqueue(cpu_usage)  # 入队
        que.dequeue()  # 出队
        y = que.items
        return x,y

    def animate(self,i):
        x,y = self.get_x_y(self.que_line1,self.cpu_usage_list[0])
        self.line.set_data(x, y)
        x1, y1 = self.get_x_y(self.que_line2, self.cpu_usage_list[1])
        self.line1.set_data(x1, y1)
        return self.line,self.line1

    def start(self):
        cpu_th = threading.Thread(target=self.cpu_usage1)
        cpu_th.setDaemon(True)
        cpu_th.start()

        # First set up the figure, the axis, and the plot element we want to animate
        self.fig = plt.figure()
        self.ax = plt.axes(xlim=(0, 60), ylim=(0, 100))
        # self.ax1 = plt.axes(xlim=(0, 60), ylim=(0, 100))
        self.line, = self.ax.plot([], [], label="cpu",color="blue",linewidth=2.5,linestyle="-")
        self.line1, = self.ax.plot([], [], label="cpu1",color="red", linewidth=2.5, linestyle="-")

        # 初始化队列
        self.que_line1 = Queue()
        self.que_line2 = Queue()
        # 队列填充60个数，监视60秒
        for i in range(0,60):
            self.que_line1.enqueue(0)
            self.que_line2.enqueue(0)
        # call the animator.  blit=True means only re-draw the parts that have changed.
        anim = animation.FuncAnimation(self.fig, self.animate, init_func=self.init,
                                       frames=200, interval=1000, blit=True)

        # anim.save('basic_animation.mp4', fps=30, extra_args=['-vcodec', 'libx264'])
        plt.legend()
        plt.title("CPU信息",fontproperties=myfont)
        plt.xlabel("时间（s）",fontproperties=myfont)
        plt.ylabel("利用率（%）",fontproperties=myfont)
        plt.show()

a = cpu_state_class()
a.start()


