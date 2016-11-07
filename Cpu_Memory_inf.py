import os
import time
import threading

class Cpu_Inf:
    def __int__(self):
        self.cpu_usage = None
        self.memory_usage = None

    def exeCmd(self,cmd):
        '''根据终端命令获取内容'''
        r = os.popen(cmd)
        text = r.read()
        r.close()
        return text

    def writeFile(self,filename,data):
        '''写入文档'''
        f = open(filename,"a")
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
        return cpu_idel,cpu_total

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

    def getInf(self):
        while True:
            self.cpu_usage = self.getCpuUsage()

            cpu_inf = 'CPU  '
            for inf in self.cpu_usage:
                cpu_inf += str(inf)+'   '
            self.memory_usage = self.getMemoryUsage()
            mem_inf = 'MEM  ' + self.memory_usage

            TIME = time.strftime("%Y/%m/%d %H:%M:%S     ", time.localtime(time.time()))
            data = TIME + cpu_inf + mem_inf + '\n'

            Time_file = time.strftime("%Y%m%d-%H")
            path = os.getcwd()
            self.writeFile(r'%s/cpu_log/%s.log' % (path, Time_file),data)

    def start(self):
        cpu_th = threading.Thread(target=self.getInf)
        cpu_th.setDaemon(True)
        cpu_th.start()
        cpu_th.join()

if __name__ == '__main__':
    cpu = Cpu_Inf()
    cpu.start()

    # while True:
    #     time.sleep(1000)
    #     pass


