# encoding=utf-8
import pytest

from weixin.request import *
from weixin.config import Config
from weixin.reply import *
from weixin.parse import WeixinMsg
from weixin.crypto import XMLMsgCryptor


common_cfg = {"token": 'A'*20, "appid": 'wx' + 'a'*16}

text_msg = """
<xml>
 <ToUserName><![CDATA[toUser]]></ToUserName>
 <FromUserName><![CDATA[fromUser]]></FromUserName>
 <CreateTime>123456789</CreateTime>
 <MsgType><![CDATA[text]]></MsgType>
 <Content><![CDATA[hello]]></Content>
 <MsgId>123456789</MsgId>
 </xml>
"""

text_msg_encrypted = """
<xml>
    <ToUserName><![CDATA[toUser]]></ToUserName>
    <Encrypt><![CDATA[ROqwv6GlhGmZfli33Ub6Kka3K2YHP/yJXQGYb2sYX1cCFZHB0RztThxWrYEcmuyhfptueEE9+6/s3XVB/3UYyDPXy6QIyCX1WW5guCoMeRCH2B5vO7/rsWrPVkxieu6VXHhS9fBHgL9HB38OlNiGn+lheU7N3+XefuM53b5CO3w51xYvOhadGGBOzM4+83Xlp5jdaA/GveEmsDdPyCH1tF5/bxdwFRbqYNGO4DXtmtOv+XexSTpPHorAiDcOGMoLdFcF5xBX3cPd9YOjIk0rZ7n0NZpyEA8s6v1AXuzS3KYxO+u3rblR+z+hK5EOypmP02cWFuR8F7rzyJJnaRvqYeGsr8yOJCq6wXoiyDvkIYBW2951AV07rs0JcNwJYy0I/t1ZqZQaIfY5XMTJfEltjzu/u9i4uAyrOYAna8Ozhcj0a3P8j7BSN/QTiCXrrAfyOiOEJYURl9iBM4LZTRiZkg==]]></Encrypt>
</xml>
"""
enc_cfg = common_cfg.copy()
enc_cfg['cryptor'] = XMLMsgCryptor(
    token='A'*20,
    appid='wx' + 'a'*16,
    enc_aeskey='E5HSDyJ78YwCSelWbCSFb4ZcXXSN1LQPdkHPblR8ilo'
    )

@pytest.mark.parametrize("config,umsg", [
    (Config(**common_cfg), text_msg),
    (Config(**enc_cfg), text_msg_encrypted),
])
def test_request(config, umsg):

    def assert_reply(msg):
        if config.cryptor:
            xml = config.cryptor.decrypt(msg.Encrypt)
            msg = WeixinMsg(xml)

        assert msg.ToUserName == 'fromUser'
        assert msg.FromUserName == 'toUser'
        assert msg.CreateTime.isdigit()

        assert msg.MsgType == 'text'
        assert msg.Content == 'hello'

    def assert_req_msg(req):
        assert req.message.ToUserName == 'toUser'
        assert req.message.FromUserName == 'fromUser'
        assert req.message.CreateTime == '123456789'
        assert req.message.MsgType == 'text'
        assert req.message.Content == 'hello'
        assert req.message.MsgId == '123456789'

    req = WeixinRequest(config, umsg)

    assert_req_msg(req)

    req.render(Text, "hello")
    resp_msg = WeixinMsg(req.get_response_xml())
    assert_reply(resp_msg)

    msg = Text("hello")
    req.response(msg)
    resp_msg = WeixinMsg(req.get_response_xml())
    assert_reply(resp_msg)
