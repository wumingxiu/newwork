#coding=utf-8
import logging
logger = logging.getLogger(__name__)
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.iostream import StreamClosedError
from tornado.tcpserver import TCPServer
from tornado.options import options, define
import socket
import json
import sys
import os
import cv2
import numpy as np
from imgserver.methods import randomImg, getImage
import time
from random import randint, uniform
from threading import Thread
# port = 9880
# define("port", default=9888, help="TCP port to listen on")



# class EchoServer(TCPServer):
#     @gen.coroutine
#     def handle_stream(self, stream, address):
#         while True:
#             try:
#                 data = yield stream.read_until(b"\n\r")
#                 logger.info("Received bytes: %s", data)
#                 if not data.endswith(b"\n"):
#                     data = data + b"\n"
#                 yield stream.write(data)
#             except StreamClosedError:
#                 logger.warning("Lost client at host %s", address[0])
#                 break
#             except Exception as e:
#                 print(e)

class SharpSever(object):
    """docstring for SharpSever"""
    def __init__(self):
        super(SharpSever, self).__init__()
        self.dirs = "IMG/sharp/oc1/"
        self.imgs = self.getAll()

    def getAll(self):
        dirlists = os.listdir(self.dirs)
        imgs = [[i, k, cv2.imread(k)] for i,k in enumerate(dirlists)]
        self.max_border = imgs[-1][0]
        self.min_border = imgs[0][0]
        return imgs

    def img_distance(self, distance):
        if not isinstance(distance, int):
            raise ValueError("input img_distance not int")
        if distance > self.max_border:
            return 'out'
        if distance < self.min_border:
            return 'min'
        print 'img name', self.imgs[distance][1]
        return self.imgs[distance][2]


class ImgServer(TCPServer):
    PARA = ('randomImg', 'IMG/G652/pk/')
    IS_RUNNING = True
    # sharpSever = SharpSever()

    @gen.coroutine
    def handle_stream(self, stream, address):
        while self.IS_RUNNING:
            try:
                data = yield stream.read_until("\n\r")#以\n\r作为字符串结束判断
                logger.warning("Received bytes: %s", data)
                data = data.strip()#去掉字符串开头和结尾的空字符
                if data == 'getimgonce':
                    self._getImgOnce(stream)
                elif data[:7] == 'change:':#如果字符串前七位为change：
                    loads = json.loads(data[7:])
                    #则更改读取图像的地址，json.loads是将json对象转成python对象生成一个字符串
                    print data
                    self.PARA = loads
                elif data[:9] == 'distance:':
                    distance = int(data[9:])
                    print 'get distance', distance
                elif data =='close':
                    self._close(stream)


            except StreamClosedError:
                logger.warning("Lost client at host %s", address[0])
                break
            except Exception as e:
                raise e

    @gen.coroutine
    def _getImgOnce(self, stream):
        img = yield self._getImgMethod(self.PARA[0],self.PARA[1])
        gen.sleep(0.1)
        img = img.tobytes() + b'\n\r\n\r'
        yield stream.write(img)

    # @gen.coroutine
    # def _getImgDistance(self, stream, distance):
    #     img = yield self.sharpSever.img_distance(stream, distance)
    #     img = img.tobytes() + b'\n\r\n\r'
    #     yield stream.write(img)

    @gen.coroutine
    def _getImgMethod(self, function = 'randomImg', para = 'IMG/G652/pk/'):#（读取方法，读取图像的地址）
        #目前默认随机读取
        # print 'getImgMehtods', function, para
        if function == 'randomImg':#随机读取图像
            return randomImg(para)
        elif function == 'getImage':
            return getImage(para)

    # @gen.coroutine
    # def _getDistanceImg(self, stream, distance):
    #     img = self.sharpSever.img_distance(distance)
    #     if isinstance(img, np.ndarray):
    #         img = img.tobytes()+ b'\n\r\n\r'
    #         yield stream.write(img)
    #     elif isinstance(img, str):
    #         cmd = 'error:' + distance + b'\n\r\n\r'
    #         yield stream.write(cmd)
    #     else:
    #         raise ValueError('img not array')


    def _close(self, stream):

        self.IS_RUNNING = False
        stream.close()
        # self.io_loop.stop()
        # self.io_loop.close()

class CameraMotorSever(TCPServer):
    IS_RUNNING = True
    MOTOR_RUNNING = True

    @gen.coroutine
    def handle_stream(self, stream, address):
        while self.IS_RUNNING:
            try:
                data = yield stream.read_until("\n\r")
                logger.info("Received bytes: %s", data)
                data = data.strip()
                if data == 'getsharp:':
                    self._send_sharp(stream)
                elif data == 'back:':
                    self.back = not self.back
                elif data == 'start:':
                    print 'get start'
                    self._get_start_timer()
                elif data =='close':
                    self._close(stream)
            except StreamClosedError:
                logger.info("Lost client at host %s", address[0])
                break
            except Exception as e:
                raise e

    def timer_thread(self):

        print 'get in timer'
        while self.MOTOR_RUNNING:
            time.sleep(0.01)
            print 'start sharp loop', self.sharp
            if self.back:
                self.sharp = self.sharp + 0.5
            else:
                self.sharp = self.sharp - 0.5

    def _get_start_timer(self):
        self.sharp = 100
        self.back = True
        timer = Thread(target=self.timer_thread)
        timer.start()


    @gen.coroutine
    def _send_sharp(self, stream):
        cmd = '{:.4f}\n\r\n\r'.format(self.sharp)
        # print 'sharp', cmd.strip()
        yield stream.write(cmd)


    def _close(self,stream):
        self.IS_RUNNING = False
        self.MOTOR_RUNNING = False
        stream.close()



class CameraMotorSeverRadom(CameraMotorSever):


    def timer_thread(self):
        print 'get in timer'
        while self.MOTOR_RUNNING:
            time.sleep(0.01)
            print 'start sharp loop {:.2f}'.format(self.sharp)
            if self.back:
                self.sharp = self.sharp + uniform(0.3,0.6)
            else:
                self.sharp = self.sharp - uniform(0.3,0.6)


def SeverMain(port):
    # options.parse_command_line()
    print 'listening on port', port
    server = ImgServer()

    server.listen(port)

    logger.info("Listening on TCP port %d", port)

    # IOLoop.instance().start()

if __name__ == "__main__":
    port=9880
    SeverMain(port)