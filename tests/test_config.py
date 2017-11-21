# encoding=utf-8
from weixin.config import *


def test_config():
    config = Config(a=0, b=1)
    assert config.a == 0
    assert config.b == 1
    
    config = Config({'a': 0, 'b': 1})
    assert config.a == 0
    assert config.b == 1

    class ConfigObject:
        A = 0
        B = 1
        a = 9
        _p = 999
    
    config = Config()
    config.from_object(ConfigObject)
    assert config.A == 0
    assert config.B == 1
    assert config.a == 9
    assert config._p == 999

    
    config = Config()
    config.from_json('{"a": 0, "b": 1}')
    assert config.a == 0
    assert config.b == 1

