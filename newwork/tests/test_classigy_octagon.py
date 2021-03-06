from setting.orderset import SETTING
SETTING().keyUpdates('octagon','centerImg')

import cv2
import numpy as np
import pdb
from pattern.getimg import getImage
from pattern.classify import OctagonClassify


def test_octagon_class_find_result():
    SETTING().keyUpdates('octagon', 'centerImg')
    img = getImage("IMG\\midoctagon\\mid1.BMP")
    result = OctagonClassify().find(img)
    keys = ['core','clad','coreResult','cladResult']
    for k in keys:
        assert k in result.keys()
    keys = ['corePoint', 'longAxisLen', 'shortAxisLen']
    for k in keys:
        assert k in result.get('coreResult',{}).keys()
        assert k in result.get('cladResult', {}).keys()

    assert isinstance(result['core'], tuple)
    assert isinstance(result['clad'], tuple)
    assert isinstance(result['cladResult']['shortPlot'], tuple)
    assert len(result['cladResult']['shortPlot']) == 2
    assert isinstance(result['cladResult']['longPlot'], tuple)
    assert len(result['cladResult']['longPlot'])== 2

def test_class_octagon_getResult():
    img = getImage("IMG\\midoctagon\\mid1.BMP")
    result = OctagonClassify().find(img)
    oca = OctagonClassify()
    oca.find(img)
    result = oca.getResult()
    assert len(result) == 5



if __name__ == '__main__':
    print  'get'
    # getthr()

    # oca = OctagonClassify().find(img)
    # plot = oca['coreResult']['plot']
    # print 'shape', plot.shape
    # print oca['coreResult']['longAxisLen'], oca['coreResult']['shortAxisLen'], oca["coreResult"]["corePoint"]
    # print oca['cladResult']['longAxisLen'], oca['cladResult']['shortAxisLen'], oca["cladResult"]["corePoint"]
    # cv2.imshow('core', plot[::4,::4])
    # cv2.waitKey()
    # cv2.imshow('clad', oca['cladResult']['plot'][::4,::4])
    # cv2.waitKey()
    # pdb.set_trace()