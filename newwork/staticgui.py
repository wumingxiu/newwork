#coding:utf-8
import logging

from imgserver.myview import Controllers

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
from setting import config
config.MODBUS_PORT = 'com14'
import sys
import os
import pdb
from setting.orderset import SETTING
Set = SETTING("test", "octagon", "centerImg")
Set['ifcamera'] = False
from PyQt4.QtGui import QPalette, QColor,QApplication
from PyQt4.QtCore import QCoreApplication, QFile
from GUI.view.view import View
from GUI.controller import Controller
from util.load import loadStyleSheet


if __name__ == '__main__':#测试台界面显示
    # sys.stdout = open('setting\\abc.txt', 'w')
    print ('len set', len(Set))
    app = QApplication(sys.argv)
    app.setStyleSheet(loadStyleSheet('main'))

    pt = QPalette()#调色板
    pt.setColor(QPalette.Background , QColor(4,159,241))#界面背景色设置为蓝色
    app.setPalette(pt)

    c = Controller(View())
    c.show()
    # sys.stdout = sys.__stdout__
    c = Controllers()
    c.show()
    sys.exit(app.exec_())
