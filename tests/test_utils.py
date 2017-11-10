# encoding=utf-8
from weixin.utils import *


def test_attrdict():
    print('test_attrdict')
    conf = AttributeDict()

    conf.attr1 = "attr1"
    conf.set("attr2", "attr2")

    assert conf.attr1 == "attr1"
    assert conf.attr2 == "attr2"

    conf.setnx("attr2", "attr")
    
    assert conf.attr2 == "attr2"

    conf.remove("attr2")
    
    assert conf.attr2 == None

    conf.setnx("attr2", "attr")
    
    assert conf.attr2 == "attr"
    assert conf.noneAttr == None


def test_get_signature():
    print('test_get_signature')
    sig = '40bd001563085fc35165329ea1ff5c5ecbdbbeef'
    
    assert sig == get_signature("1", "2", "3")
    assert sig == get_signature("1", "2", "3")
    assert sig == get_signature("1", "2", "3")
    

def test_join_sequence():
    print('test_join_sequence')
    assert join_sequence(['1', '2', '3']) == '123'
    assert join_sequence([b'1', b'2', b'3']) == b'123'
    assert join_sequence(iter('123')) == '123'


def test_to_str():
    print('test_to_str')
    assert to_str(123) == '123'
    assert to_str(123.33) == '123.33'
    assert to_str(b'123') == '123'
    assert to_str('123') == '123'
    assert to_str('是') == '是'
    assert to_str(b'\xe6\x98\xaf') == '是'


def test_to_bytes():
    print('test_to_bytes')
    assert to_bytes(123) == b'123'
    assert to_bytes(123.33) == b'123.33'
    assert to_bytes(b'123') == b'123'
    assert to_bytes('123') == b'123'
    assert to_bytes('是') == b'\xe6\x98\xaf'
    assert to_bytes(b'\xe6\x98\xaf') == b'\xe6\x98\xaf'
    

if __name__ == "__main__":
    test_attrdict()
    test_get_signature()
    test_join_sequence()
    test_to_str()
    test_to_bytes()
