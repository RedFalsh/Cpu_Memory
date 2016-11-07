#!/usr/bin/python3
# coding=utf-8

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from main import  Ui_MainWindow
import sys

from get_inf import Get
from matplot import Cpu_plot
from matplot import Mem_plot
class MainDlg(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        timer = QTimer(self)
        timer.timeout.connect(self.update_show)
        timer.start(1000)

        self.get = Get()

        self.label_sys = QLabel()
        self.verticalLayout_cpu_plt.addWidget(self.label_sys)

        CPU = Cpu_plot(QWidget(self))
        self.verticalLayout_cpu_plt.addWidget(CPU)

        MEM = Mem_plot(QWidget(self))
        self.verticalLayout_cpu_plt.addWidget(MEM)


    def update_show(self):
        alread_run, free_usage = self.get.get_sys_run_time()
        label = alread_run + '      空闲率：%.2f%s'%(free_usage,'%')

        sda_list = self.get.get_sda()
        sda_str = ''
        for sda in sda_list:
            sda_str = sda_str + '硬盘：%s     容量：%s      已用：%s      可用：%s       已用%s:%s'\
                      %(sda[0],sda[1],sda[2],sda[3],'%',sda[4]) + '\r\n'

        self.label_sys.setText(label + '\r\n' + sda_str)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = MainDlg()
    dlg.show()
    sys.exit(app.exec_())
