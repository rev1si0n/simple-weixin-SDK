# encoding=utf-8
from weixin.crypto import*


xml_cryptor = XMLMsgCryptor('wx' + 'a'*16, 'A'*20, 'A'*43)


def test_xmlmsg_decrypt():
    enc_msg = "ElQfgclqivmqOxQpx6eCEvraIg1Fvwg0t+mhrBPU"\
              "4Xm0nHCuv9xMM5JsIh7OxIsybzfOeUvxog7fg/sT"\
              "Z6rC4/8IXTj2UWD73Au6m0yeZxv2DbjuUHqpVJAL"\
              "Xc3rC7E3f1RdCZ0cdzROOR9sg0aP3ArTUNB9ixIN"\
              "P6hGfzf3RHCCAhkUQ5wR0UP2NElM7XgN4702n7WM"\
              "yWO9uYna583pm/I3DOriC3WzG6JdPbhBuoAseisz"\
              "7xCA59R3lFg+XazBsia60auOehb069IvUy24tIj+"\
              "OcdzfbMui4efTHI7ogYWbVKFRG4W2ghQ8p0cymFk"\
              "yukHGMCdccZzAIssatB1RNhuaqQ0fOXIji486b5r"\
              "g8/OlXIuDFCwkoWFMQaZycJa/bhjSmn+ygYkmqrM"\
              "VC1jtmHZM4qmNvL8WXQ1PrP6X/CXU6/iIbeF1yjG"\
              "pjOE4xfCKsOnL3jQayzfUny3iWgT4A=="
    
    result = xml_cryptor.decrypt(enc_msg)

    assert all([
        'toUser' in result,
        'fromUser' in result,
        '123456789' in result,
        'text' in result,
        'content' in result,
    ])



def test_xmlmsg_en_decrypt():
    msg = \
    "<xml>"\
    "<ToUserName><![CDATA[toUser]]></ToUserName>"\
    "<FromUserName><![CDATA[fromUser]]></FromUserName>"\
    "<CreateTime>123456789</CreateTime>"\
    "<MsgType><![CDATA[text]]></MsgType>"\
    "<Content><![CDATA[content]]></Content>"\
    "</xml>"

    param_dict = xml_cryptor.encrypt(msg)
    de_result = xml_cryptor.decrypt(param_dict['enctext'])

    assert de_result == msg
