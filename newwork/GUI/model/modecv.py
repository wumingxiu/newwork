#coding:utf-8
import collections
import time
from threading import Thread
import cv2
import copy
import numpy as np
from PyQt4.QtCore import QObject, pyqtSignal
from .datahand import session_add,ResultSheet
from setting.orderset import SETTING
from pattern.exception import ClassCoreError, ClassOctagonError

Set = SETTING('octagon')
setGet = Set.get('ifcamera', False)
fiberType = Set.get('fiberType',"G652")
print 'fibertype',fiberType,'setget', setGet
if setGet:
    from SDK.mdpy import GetRawImg
else:
    #from SDK.mdpytest import DynamicGetRawImgTest as GetRawImg
    # from  SDK.mdpy import GetRawImgTest as GetRawImg
    #当摄像头关闭时，图像从文件夹读取
    from imgserver.model import DynamicGetRawImgTest as GetRawImg
    print 'script don\'t open camera'

from pattern.edge import ExtractEdge
from report import pdf
from pattern.classify import classifyObject

from pattern.sharp import IsSharp
from pattern.draw import DecorateImg, drawCoreCircle, decorateMethod
from SDK.oceanoptics import OceanOpticsTest
from util.toolkit import Cv2ImShow, Cv2ImSave

import serial
from pattern.sharper import AbsFocuser
from util.timing import timing
from util.filter import AvgResult
from util.loadimg import sliceImg
import sys


from collections import Iterable

import logging
logger = logging.getLogger(__name__)

class ModelCV(Thread, QObject):
    """docstring for Model"""
    # 建立多个信号槽
    returnImg = pyqtSignal(object, object,object)
    returnATImg = pyqtSignal(object, object)
    resultShowCV = pyqtSignal(object)
    resultShowAT = pyqtSignal(object)
    returnCoreLight = pyqtSignal(object, object)

    def __init__(self, ):
        Thread.__init__(self)
        QObject.__init__(self)
        super(ModelCV, self).__init__()
        self.setDaemon(True)
        self.IS_RUN = True
        self.isSharp = IsSharp()
        self.show = Cv2ImShow()
        self.save = Cv2ImSave()
        self.eresults = False
        self.result2Show = {}
        self.decorateMethod = decorateMethod("G652")
        self.getRawImg = GetRawImg()
        self.imgmaxlen = 5
        self.imgQueue = collections.deque(maxlen = self.imgmaxlen)
        self.fiberResult = {}
        self.Oceanoptics = OceanOpticsTest()
        self.classify = classifyObject('G652')
        self.pdfparameter = SETTING()['pdfpara']
        self.dbparameter = SETTING()['dbpara']
        # self.sharps = collections.deque(maxlen=15)
        try:
            # self.focuser = LiveFocuser()
            self.focuser = AbsFocuser()
            # self.focuser.start()
        except serial.serialutil.SerialException as e:
            print e


    def run(self):
        while self.IS_RUN:
            img = self.getRawImg.get()
            if not isinstance(img, np.ndarray):
                break
            self.img = img.copy()
            self.imgQueue.append(self.img)
            # self.sharp = "%0.2f"%self.isSharp.isSharpDiff(list(self.imgQueue))
            sharp_ = "%0.2f" % (self.isSharp.issharpla(img[::,::,0])*10)
            lights = "%0.2f" % self.sum_light()
            self.sharp = sharp_

            # if hasattr(self,'focuser'):
            #     self.focuser.get_sharp(self.sharp)
            # plotResults = (self.ellipses, self.result)
            self._greenLight(img)
            colorImg = self._decorateImg(img)
            self.returnImg.emit(colorImg[::4,::4].copy(), self.sharp, lights)


    def mainCalculate(self):
        def _calcImg():
            try:
                # img.tofile("tests\\data\\tests\\midimg{}.bin".format(str(int(time.time()))[-3:]))
                self.imgQueue.clear()
                results = []
                while len(self.imgQueue) != 5:
                    time.sleep(0.1)
                for img in list(self.imgQueue):
                    self.eresults = self.classify.find(img)
                    result = self.eresults["showResult"]
                    print 'get result', result
                    results.append(result)
                self._emitCVShowResult(AvgResult(results))
            except ClassCoreError as e:
                print e,'class core error'
                self.resultShowCV.emit('error')
                return
            except ValueError as e:
                print e
                self.resultShowCV.emit('error')
                return
            except Exception as e:
                logger.exception(e)
        Thread(target = _calcImg).start()


    def updateClassifyObject(self, obj = 'G652'):
        self.classify = classifyObject(obj)
        self.eresults = False
        self.result2Show = False
        self.decorateMethod = decorateMethod(obj)


    def _decorateImg(self,img):
        """"mark the circle and size parameter"""
        img = drawCoreCircle(img)
        # print 'decorate in ',not (ellipses  or self.decorateMethod), ellipses , result , self.decorateMethod
        if self.result2Show:
            img = self.decorateMethod(img, self.result2Show)
        return img


    def exit(self):
        print "unInit"
        self.IS_RUN = False
        time.sleep(0.5)
        self.getRawImg.unInitCamera()

    def initGUI(self):
        existence = {}


    def attenuationTest(self, length):
        wave, powers = self.Oceanoptics.getData(length)
        self._emitATShowResult(wave, powers)
        self.returnATImg.emit(wave, powers)

    def _emitATShowResult(self, wave, powers):
        waveLimit = wave[-1] - wave[0]
        waveMax = np.max(powers)
        waveMin = np.min(powers)
        waveAvg = np.average(powers)
        # print waveLimit, waveMax, waveMin, waveAvg
        text = (u'''波长范围：    {:%0.2f}\n'''
            u'''最大值：      {:%0.2f}\n'''
            u'''最小值：      {:%0.2f}\n'''
            u'''平均值：      {:%0.2f}\n''')
        text = text.format(waveLimit,waveMax,waveMin,waveAvg)
        self.resultShowAT.emit(text)


    def _emitCVShowResult(self, result):
        sharp = self.sharp
        self.result2Show = copy.deepcopy(self.eresults)
        self.result2Show["showResult"] = result
        if not hasattr(result, '__getitem__'):
            self.resultShowCV.emit('error')
            return
        result = result[1:]+result[:1]
        keys = ('corediameter','claddiameter','coreroundness',
                'cladroundness','concentricity')
        str_pdf_para_from_result = {k: '%0.2f'%r for k,r in zip(keys,result)}
        str_pdf_para_from_result.update({'sharpindex': sharp})
        self.pdfparameter.update(str_pdf_para_from_result)

        raw_db_data_from_result = {k: r for k,r in zip(keys,result)}
        raw_db_data_from_result.update({'sharpindex': sharp})
        # if None in result:
        #     for i,v in enumerate(result):
        #         if not v:
        #             result[i] = '-1'
        self.dbparameter.update(raw_db_data_from_result)
        text = (u'''纤芯直径：    {:0.2f}\n'''
            u'''包层直径：    {:0.2f}\n'''
            u'''纤芯不圆度：  {:0.2f}\n'''
            u'''包层不圆度：  {:0.2f}\n'''
            u'''芯包同心度：  {:0.2f}''')
        text = text.format(*result)
        logger.exception(text)
        self.resultShowCV.emit(text)




    def _greenLight(self, img):
        if isinstance(img, np.ndarray):
            corey, corex = SETTING()["corepoint"]
            minRange, maxRange = SETTING()["coreRange"]
            green = sliceImg(img[::, ::, 1], (corex, corey), maxRange)
            blue = sliceImg(img[::, ::, 2], (corex, corey), maxRange)
            self.allblue = img[::,::,2].sum()/255

            self.green = green.sum() / 255
            self.blue = blue.sum() / 255
            self.allgreen = img[::, ::, 1].sum() / 255 - self.green
            self.pdfparameter['corelight'] = "%0.2f" % self.blue
            self.pdfparameter['cladlight'] = "%0.2f" % self.allgreen
            self.returnCoreLight.emit("%0.2f" % (self.blue), "%0.2f" % (self.allgreen))
            # self.returnCladLight.emit()

    def fiberTypeMethod(self, key):
        SETTING().keyUpdates(key)

    def focus(self):
        print 'get focuser start'
        self.focuser.start()

    #
    # def _getImg(self):
    #     img = self.getRawImg.get()
    #     # img = self.getRawImg.bayer2BGR(img)
    #     self.img = img.copy()
    #     # self.imgQueue.append(img)
    #     # print 'imgqueue', len(self.imgQueue)
    #     # self.sharpQueue.append(img)
    #     return img

    # @timing
    # def _getDifferImg(self):
    #     imgs = list(self.imgQueue)
    #     imgAllor = np.zeros(imgs[0].shape[:2], dtype=imgs[0].dtype)
    #     for img in imgs:
    #         img = ExtractEdge().run(img)
    #         imgAllor = cv2.bitwise_or(imgAllor, img)
    #     img = imgs[-1]
    #     print 'img.shape', img.shape
    #     return img

    # @timing
    # def _toClassify(self, img):
    #     print 'get img type', img.shape, img.dtype
    #     self.eresults = self.classify.find(img)
    #     self.result = self.eresults["showResult"]
    #     print 'get ellipses', self.result
    #     if self.result:
    #         SETTING()['tempLight'].append([int(self.green), float(self.result[1])])
    #
    #     return self.result


    def sum_light(self):
        _ = self.img[::,::,0].sum()#统计图像中的所有像素
        _ = _//(2592*1944)
        return _

