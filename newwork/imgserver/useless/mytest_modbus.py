#coding=utf-8
from threading import Thread
import serial
import  emit
from PyQt4 import  QtGui
from PyQt4.QtCore import QString, pyqtSignal, QObject
from PyQt4.QtGui import QMainWindow
from dialogUI import Ui_Dialog as new_MainWindow

from imgserver.dialog_view import Dialog
from util.observer import MySignal

class Slave(Thread,QObject):
    emit_dir = pyqtSignal(object)  # 信号槽
    def __init__(self):
        super(Slave, self).__init__()
        QObject.__init__(self)
        # 串口为com14，波特率为19200，超时0.05，校验位
        # timeout:超时时间到，执行下一条语句，如果不设置timeout，读不到数据，程序将死在这个地方。
        self.ser = serial.Serial('com14', 19200, timeout=0.05, parity= 'E')
        self.RUNNING = True

        print(self.ser.parity)#打印当前的奇偶校验设置

    def run(self):
        while self.RUNNING:
            try:
                readed = self.ser.read(100)
            except Exception as e:
                return e

            if readed:
                #self.data.emit(readed)
                _str = 'get write '+ " ".join("{:02x}".format(ord(c)) for c in readed)  # 将字符串转化为十六进制
                self.mystr= str(_str)
                print self.mystr
                self.emit_dir.emit(self.mystr)

        self.ser.close()

    def close(self):
        print('get slave close')
        self.RUNNING = False

class Controller_times(object):

    def __init__(self):

        self.slave = Slave()  # 初始化Model
        self.slave.start()
        self.view = Dialog()  # 初始化窗口
        self.slave.emit_dir.connect(self.view.initUI)  # 将信号槽内容发送到窗口的text当中


    def dialog_show(self):

        self.view.show()  # 窗口显示

#if __name__ == '__main__':#注意缩进

 #   import sys

  #  app = QtGui.QApplication(sys.argv)

#    slave=Slave()
 #   slave.start()

 #   sys.exit(app.exec_())










