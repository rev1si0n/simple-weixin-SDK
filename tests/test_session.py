# encoding=utf-8
import time
from weixin.config import *
from weixin.storage import *
from weixin.session import *


request = Config(
    message=Config(FromUserName="openid"),
    config=Config(storage=RedisStorage())
)

def test_session():
    session = Session(request)

    session['k1'] = 'v1'
    session['k2'] = 'v2'
    session('k3', 'v3')
    session('k4', 'v4')
    session('你好', '不好')

    session.save(expires=30)

    session = Session(request)
    assert session['k1'] == 'v1'
    assert session['k2'] == 'v2'
    assert session('k3') == 'v3'
    assert session('k4') == 'v4'
    assert session('你好') == '不好'
    
    assert session['key_not_exist'] == None
    assert session('key_not_exist') == None

    session.destroy()

    session = Session(request)
    assert session['k1'] == None
    assert session('k1') == None

    session('exp', 12345)
    session.save(expires=1)

    time.sleep(3)
    session = Session(request)
    assert session('exp') == None
