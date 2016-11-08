import sys
import random

import matplotlib
matplotlib.use("Qt5Agg")

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.font_manager as fm
import matplotlib.dates as dates

from get_inf import Get
import threading
import time
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

class MyMplCanvas(FigureCanvas):
    """这是一个窗口部件，即QWidget（当然也是FigureCanvasAgg）"""
    def __init__(self, parent=None):

        # fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111)

        # 每次plot()调用的时候，我们希望原来的坐标轴被清除(所以False)
        self.axes.hold(False)

        self.show_line()

        #
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def show_line(self):
        pass

###############################################################
#                         曲线                                #
###############################################################
# 查看字体命令： fc-list :lang=zh
import os

path = os.getcwd()
myfont = fm.FontProperties(fname='%s/font/simsun.ttc'%path)
class Cpu_plot(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QTimer(self)
        timer.timeout.connect(self.update_figure)
        time.sleep(1)
        timer.start(1000)

    def show_line(self):
        self.get = Get()
        self.get.start()
        self.plt_cpu = plt.subplot(111)

        self.line, = self.plt_cpu.plot([], [], label='cpu', color='blue', linewidth=2.5, linestyle="-")
        self.plt_cpu.set_xlim(0, 60)
        self.plt_cpu.set_ylim(0, 100)
        self.plt_cpu.grid(True)
        self.plt_cpu.legend()
        self.plt_cpu.set_ylabel("CPU利用率（%）", fontproperties=myfont)

        self.que = Queue()

    def get_x_y(self, que, cpu_usage):
        x = np.linspace(1, 60, 60)
        que.enqueue(cpu_usage)  # 入队
        que.dequeue()  # 出队
        y = que.items
        return x, y

    def update_figure(self):

        if self.get.cpu_usage:
            self.plt_cpu.set_title("CPU利用率:%s%s" % (self.get.cpu_usage[0],'%'), fontproperties=myfont)
            x, y = self.get_x_y(self.que, self.get.cpu_usage[0])
            self.line.set_data(x, y)
            self.draw()


class Mem_plot(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def show_line(self):
        self.get = Get()
        self.plt_mem = plt.subplot(111)
        self.line, = self.plt_mem.plot([], [], label='Memory', color='red', linewidth=2.5, linestyle="-")

        self.plt_mem.set_xlim(0, 60)
        self.plt_mem.set_ylim(0, 100)
        self.plt_mem.grid(True)
        self.plt_mem.legend()
        self.plt_mem.set_ylabel("内存利用率（%）", fontproperties=myfont)

        self.que = Queue()

    def get_x_y(self, que, item):
        x = np.linspace(1, 60, 60)
        que.enqueue(item)  # 入队
        que.dequeue()  # 出队
        y = que.items
        return x, y

    def update_figure(self):

        Mem_usage,Mem_used,Mem_free,Mem_total = self.get.getMemoryUsage()
        inf = "内存利用率：%s%s 总内存：%dM 使用中：%dM 可用：%dM"%(Mem_usage,'%',Mem_total,Mem_used,Mem_free)

        self.plt_mem.set_title("%s"%inf, fontproperties=myfont)
        x, y = self.get_x_y(self.que, Mem_usage)
        self.line.set_data(x, y)
        self.draw()
