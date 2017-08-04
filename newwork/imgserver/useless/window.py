#coding=utf-8
from PyQt4 import  QtGui
import pickle
import os
import socket
import json


class Frame(QtGui.QWidget):
    def __init__(self,parent=None):
        super(Frame,self).__init__(parent)

        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.connect(("127.0.0.1", 9880))

        inputLabel=QtGui.QLabel(u"请输入：")
        self.inputLine=QtGui.QLineEdit()

        self.loadButton=QtGui.QPushButton(u"&选择")
        self.loadButton.setToolTip(u"从文件夹中选择（选中的为文件夹而不是单一文件）")
        self.loadButton.clicked.connect(self.loadContact)

        self.okButton = QtGui.QPushButton(u"&确认")
        self.okButton.setToolTip(u"确定该文件")
        self.okButton.clicked.connect(self.okContact)

        mainLayout=QtGui.QGridLayout()
        mainLayout.addWidget(inputLabel,0,0)
        mainLayout.addWidget(self.inputLine,0,1)
        mainLayout.addWidget(self.loadButton,0,2)
        mainLayout.addWidget(self.okButton,1,1)


        self.setLayout(mainLayout)
        self.setWindowTitle("choose")



    def loadContact(self):
        self.fileName=QtGui.QFileDialog.getExistingDirectory(self,"Open IMG ",'',)#读取目录
        #那么他就不一定是最后一级文件夹，还要判断文件夹内包含的文件是否为图像文件


        for f in os.listdir(self.fileName):

           if f.endswith('.BMP'):
               self.inputLine.setText(self.fileName)
           else:
               QtGui.QMessageBox.information(self, u"文件读取失败",
                                             u" \"%s\"不是BMP图像文件夹" % self.fileName)
               return

    def okContact(self):
        js=('randomImg',str(self.fileName))

        #print sys.argv
        #assert len(sys.argv) == 3
        #para = sys.argv[1:]
        #cmd='change:'+js.encode(para)+'\n\r'

        cmd = 'change:' + json.dumps(js) + '\n\r'
        self.sock.sendall(cmd)






if __name__ == '__main__':#注意缩进

    import sys

    app = QtGui.QApplication(sys.argv)

    frame = Frame()
    frame.show()

    sys.exit(app.exec_())

