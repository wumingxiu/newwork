from setting.orderset import SETTING, singleton
SETTING().keyUpdates('G652')

def test_other_set():
    s = SETTING('G652')
    print s.store
    assert 'G652' == s.get('fiberType')
    s = SETTING('octagon')
    print s.store
    print 'singleton2', id(s)
    assert 'octagon' != s.get('fiberType')

def test_get_new_value():
    s = SETTING("printline")
    s["newkey"] = True
    assert s.get("newkey")

def test_updateSets_args():
    s = SETTING("Default")
    s.updates()
    assert "set" not in s.keys()
    assert "testsetdict" not in s.keys()
    s.updates("set", {"testsetdict": "dict"})
    assert s.get("testset") == ".json"
    assert s.get("testsetdict") == "dict"

def test_updateSets_kwargs():
    s = SETTING("Default")
    assert 'testkwargs' not in s.keys()
    s.updates(testkwargs='get')
    assert s.get('testkwargs') == 'get'

def test_updateSets_Exception():
    s = SETTING("Default")
    try:
        s.updates(1)
    except Exception, e:
        assert isinstance(e, ValueError)


def test_updatekeys():
    s = SETTING()
    s.keyUpdates('20/400')
    assert s.get('fiberType') == "20/400"
    s.keyUpdates('octagon')
    assert s.get('fiberType') == "octagon"
    s.keyUpdates('G652')
    assert s.get('fiberType') == "G652"



if __name__ == '__main__':
    # from setting.orderset import SETTING
    # s = SETTING({})
    # print s
    # del SETTING
    # import SETTING
    # from setting.orderset import SETTING
    pass