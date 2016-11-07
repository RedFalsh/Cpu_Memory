
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as dates
#查看字体命令： fc-list :lang=zh
myfont = fm.FontProperties(fname='/usr/share/fonts/truetype/wqy/wqy-microhei.ttc')
class cpu_showtime:
    def __init__(self):
        # First set up the figure, the axis, and the plot element we want to animate
        # self.fig = plt.figure()
        # self.ax = plt.axes(xlim=(0, 60), ylim=(0, 100))
        # self.line_cpu, = self.ax.plot([], [], label='cpu', color='blue', linewidth=2.5, linestyle="-")
        #
        x = np.linspace(1, 60, 60)
        # y = np.linspace(1, 60, 60)
        #
        # self.line_cpu.set_data(x, y)

    def exeCmd(self,cmd):
        '''根据终端命令获取内容'''
        r = os.popen(cmd)
        text = r.read()
        r.close()
        return text

    def cat_fileList(self):
        '''获取文件列表'''
        path = os.getcwd()
        log_path = path + '/cpu_log/'
        file_list = self.exeCmd("ls %s" % log_path).split('\n')
        for file in file_list:
            if file:
                self.cat_fileContent(log_path, file)

    def cat_fileContent(self):
        '''获取cpu日志文件内容'''
        path = os.getcwd()
        log_path = path + '/cpu_log/'
        file_list = self.exeCmd("ls %s" % log_path).split('\n')
        filename = file_list[1]
        list = self.exeCmd("cat %s%s | awk '{print $2,$4,$10}'"%(log_path,filename)).split('\n')
        cpu_inf = []
        mem_inf = []

        start_time = list[0][0:8]
        end_time = list[len(list)-2][0:8]

        for li in list:
            if li:
                inf = li.split(' ')
                cpu_inf.append(inf[1])
                mem_inf.append(inf[2])
        return cpu_inf, mem_inf,start_time,end_time

    def start(self):
        cpu_inf, mem_inf, start_time, end_time = self.cat_fileContent()
        idx = pd.date_range('%s'%start_time, periods=len(cpu_inf), freq='S')
        s = pd.Series(cpu_inf, index=idx)
        # fig, ax = plt.subplots()
        fig = plt.figure()
        ax = plt.axes(ylim=(0, 100))
        ax.plot_date(idx.to_pydatetime(), s, '-')

        # 坐标轴主刻度标签
        ax.xaxis.set_minor_locator(dates.AutoDateLocator())
        # 坐标轴次刻度标签
        ax.xaxis.set_minor_formatter(dates.DateFormatter('\n\n%Y/%m/%d'))
        ax.xaxis.grid(True, which="minor")
        ax.yaxis.grid()
        # ax.xaxis.set_major_locator(dates.MonthLocator())
        # ax.xaxis.set_major_formatter(dates.DateFormatter('\n%b\n%Y'))
        plt.tight_layout()
        # plt.show()

        plt.legend()
        plt.title("CPU信息", fontproperties=myfont)
        plt.xlabel("时间（s）", fontproperties=myfont)
        plt.ylabel("利用率（%）", fontproperties=myfont)
        plt.show()

if __name__ == '__main__':
    cpu = cpu_showtime()
    cpu.cat_fileContent()
    cpu.start()
    # cpu.start()