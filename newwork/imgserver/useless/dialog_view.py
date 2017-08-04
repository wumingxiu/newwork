#coding=utf-8
from PyQt4.QtCore import QObject
from PyQt4.QtGui import QMainWindow
from PyQt4 import  QtGui

from dialogUI import Ui_Dialog as new_MainWindow



class Dialog(QMainWindow, new_MainWindow,QObject):

    def __init__(self, ):
        super(Dialog, self).__init__()
        self.setupUi(self)


    def initUI(self,mystr):
        #slave=Slave()
        #slave.start()
        self.textEdit.setText(mystr)



