# encoding=utf-8
from weixin.parse import *


def test_text_msg():
    print('test_text_msg')
    xml = """<xml>
     <ToUserName><![CDATA[toUser]]></ToUserName>
     <FromUserName><![CDATA[fromUser]]></FromUserName>
     <CreateTime>123456789</CreateTime>
     <MsgType><![CDATA[text]]></MsgType>
     <Content><![CDATA[你好]]></Content>
     <MsgId>123456789</MsgId>
     </xml>
     """
    msg = WeixinMsg(xml)
    
    assert msg.ToUserName == 'toUser'
    assert msg.FromUserName == 'fromUser'
    assert msg.CreateTime == '123456789'
    assert msg.MsgId == '123456789'
    
    assert msg.MsgType == 'text'
    assert msg.Content == '你好'


def test_image_msg():
    print('test_image_msg')
    xml = """<xml>
     <ToUserName><![CDATA[toUser]]></ToUserName>
     <FromUserName><![CDATA[fromUser]]></FromUserName>
     <CreateTime>123456789</CreateTime>
     <MsgType><![CDATA[image]]></MsgType>
     <PicUrl><![CDATA[url]]></PicUrl>
     <MediaId><![CDATA[media_id]]></MediaId>
     <MsgId>123456789</MsgId>
     </xml>
     """
    msg = WeixinMsg(xml)
    
    assert msg.ToUserName == 'toUser'
    assert msg.FromUserName == 'fromUser'
    assert msg.CreateTime == '123456789'
    assert msg.MsgId == '123456789'
    
    assert msg.MsgType == 'image'
    assert msg.PicUrl == 'url'
    assert msg.MediaId == 'media_id'


def test_voice_msg():
    print('test_voice_msg')
    xml = """<xml>
    <ToUserName><![CDATA[toUser]]></ToUserName>
    <FromUserName><![CDATA[fromUser]]></FromUserName>
    <CreateTime>123456789</CreateTime>
    <MsgType><![CDATA[voice]]></MsgType>
    <MediaId><![CDATA[media_id]]></MediaId>
    <Format><![CDATA[Format]]></Format>
    <MsgId>123456789</MsgId>
    </xml>
     """
    msg = WeixinMsg(xml)
    
    assert msg.ToUserName == 'toUser'
    assert msg.FromUserName == 'fromUser'
    assert msg.CreateTime == '123456789'
    assert msg.MsgId == '123456789'
    
    assert msg.MsgType == 'voice'
    assert msg.MediaId == 'media_id'
    assert msg.Format == 'Format'


def test_video_msg():
    print('test_video_msg')
    xml = """<xml>
    <ToUserName><![CDATA[toUser]]></ToUserName>
    <FromUserName><![CDATA[fromUser]]></FromUserName>
    <CreateTime>123456789</CreateTime>
    <MsgType><![CDATA[video]]></MsgType>
    <MediaId><![CDATA[media_id]]></MediaId>
    <ThumbMediaId><![CDATA[thumb_media_id]]></ThumbMediaId>
    <MsgId>123456789</MsgId>
    </xml>
     """
    msg = WeixinMsg(xml)
    
    assert msg.ToUserName == 'toUser'
    assert msg.FromUserName == 'fromUser'
    assert msg.CreateTime == '123456789'
    assert msg.MsgId == '123456789'
    
    assert msg.MsgType == 'video'
    assert msg.MediaId == 'media_id'
    assert msg.ThumbMediaId == 'thumb_media_id'


def test_shortvideo_msg():
    print('test_shortvideo_msg')
    xml = """<xml>
    <ToUserName><![CDATA[toUser]]></ToUserName>
    <FromUserName><![CDATA[fromUser]]></FromUserName>
    <CreateTime>123456789</CreateTime>
    <MsgType><![CDATA[shortvideo]]></MsgType>
    <MediaId><![CDATA[media_id]]></MediaId>
    <ThumbMediaId><![CDATA[thumb_media_id]]></ThumbMediaId>
    <MsgId>123456789</MsgId>
    </xml>
     """
    msg = WeixinMsg(xml)
    
    assert msg.ToUserName == 'toUser'
    assert msg.FromUserName == 'fromUser'
    assert msg.CreateTime == '123456789'
    assert msg.MsgId == '123456789'
    
    assert msg.MsgType == 'shortvideo'
    assert msg.MediaId == 'media_id'
    assert msg.ThumbMediaId == 'thumb_media_id'


def test_location_msg():
    print('test_location_msg')
    xml = """<xml>
    <ToUserName><![CDATA[toUser]]></ToUserName>
    <FromUserName><![CDATA[fromUser]]></FromUserName>
    <CreateTime>123456789</CreateTime>
    <MsgType><![CDATA[location]]></MsgType>
    <Location_X>23.134521</Location_X>
    <Location_Y>113.358803</Location_Y>
    <Scale>20</Scale>
    <Label><![CDATA[位置信息]]></Label>
    <MsgId>123456789</MsgId>
    </xml>
     """
    msg = WeixinMsg(xml)
    
    assert msg.ToUserName == 'toUser'
    assert msg.FromUserName == 'fromUser'
    assert msg.CreateTime == '123456789'
    assert msg.MsgId == '123456789'
    
    assert msg.MsgType == 'location'
    assert msg.Location_X == '23.134521'
    assert msg.Location_Y == '113.358803'
    assert msg.Scale == '20'
    assert msg.Label == '位置信息'


def test_link_msg():
    print('test_link_msg')
    xml = """<xml>
    <ToUserName><![CDATA[toUser]]></ToUserName>
    <FromUserName><![CDATA[fromUser]]></FromUserName>
    <CreateTime>123456789</CreateTime>
    <MsgType><![CDATA[link]]></MsgType>
    <Title><![CDATA[公众平台官网链接]]></Title>
    <Description><![CDATA[公众平台官网链接]]></Description>
    <Url><![CDATA[url]]></Url>
    <MsgId>123456789</MsgId>
    </xml>
     """
    msg = WeixinMsg(xml)
    
    assert msg.ToUserName == 'toUser'
    assert msg.FromUserName == 'fromUser'
    assert msg.CreateTime == '123456789'
    assert msg.MsgId == '123456789'
    
    assert msg.MsgType == 'link'
    assert msg.Title == '公众平台官网链接'
    assert msg.Description == '公众平台官网链接'
    assert msg.Url == 'url'


if __name__ == "__main__":
    test_text_msg()
    test_image_msg()
    test_voice_msg()
    test_video_msg()
    test_shortvideo_msg()
    test_location_msg()
    test_link_msg()
