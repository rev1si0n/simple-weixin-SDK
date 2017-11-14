# encoding=utf-8
from weixin.reply import *
from weixin.parse import WeixinMsg


from_msg = WeixinMsg("""<xml>
<ToUserName><![CDATA[toUser]]></ToUserName>
<FromUserName><![CDATA[fromUser]]></FromUserName>
<CreateTime>123456789</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[你好]]></Content>
<MsgId>123456789</MsgId>
</xml>
"""
)


def test_text_reply():
    msg = Text("不好")
    msg.postmark(from_msg)
    
    msg = WeixinMsg(msg.xml)
    
    assert msg.ToUserName == 'fromUser'
    assert msg.FromUserName == 'toUser'
    assert msg.CreateTime.isdigit()

    assert msg.MsgType == 'text'
    assert msg.Content == '不好'


def test_image_reply():
    msg = Image("media_id")
    msg.postmark(from_msg)
        
    msg = WeixinMsg(msg.xml)
    
    assert msg.ToUserName == 'fromUser'
    assert msg.FromUserName == 'toUser'
    assert msg.CreateTime.isdigit()

    assert msg.MsgType == 'image'
    assert msg.Image['MediaId'] == 'media_id'


def test_voice_reply():
    msg = Voice("media_id")
    msg.postmark(from_msg)
    
    msg = WeixinMsg(msg.xml)

    assert msg.ToUserName == 'fromUser'
    assert msg.FromUserName == 'toUser'
    assert msg.CreateTime.isdigit()

    assert msg.MsgType == 'voice'
    assert msg.Voice['MediaId'] == 'media_id'


def test_video_reply():
    msg = Video('media_id', title="test", description="test")
    msg.postmark(from_msg)
    
    msg = WeixinMsg(msg.xml)

    assert msg.ToUserName == 'fromUser'
    assert msg.FromUserName == 'toUser'
    assert msg.CreateTime.isdigit()

    assert msg.MsgType == 'video'
    assert msg.Video['MediaId'] == 'media_id'
    assert msg.Video['Title'] == 'test'
    assert msg.Video['Description'] == 'test'


def test_music_reply():
    msg = Music(
        'thumb_media_id',
        url="http://m",
        hq_url="http://hqm",
        title="test",
        description="test"
    )
    msg.postmark(from_msg)
    
    msg = WeixinMsg(msg.xml)

    assert msg.ToUserName == 'fromUser'
    assert msg.FromUserName == 'toUser'
    assert msg.CreateTime.isdigit()

    assert msg.MsgType == 'music'
    assert msg.Music['ThumbMediaId'] == 'thumb_media_id'
    assert msg.Music['Title'] == 'test'
    assert msg.Music['Description'] == 'test'
    assert msg.Music['MusicUrl'] == 'http://m'
    assert msg.Music['HQMusicUrl'] == 'http://hqm'


def test_article_reply():

    def assert_msg(amsg):
        assert amsg.ToUserName == 'fromUser'
        assert amsg.FromUserName == 'toUser'
        assert amsg.CreateTime.isdigit()
        assert amsg.MsgType == 'news'
        assert amsg.ArticleCount == '2'

        assert amsg.Articles['item'][0]['Title'] == 'test'
        assert amsg.Articles['item'][0]['Description'] == 'test'
        assert amsg.Articles['item'][0]['PicUrl'] == 'http://img'
        assert amsg.Articles['item'][0]['Url'] == 'http://ar'
        
        assert amsg.Articles['item'][1]['Title'] == 'test2'
        assert amsg.Articles['item'][1]['Description'] == 'test2'
        assert amsg.Articles['item'][1]['PicUrl'] == 'http://img2'
        assert amsg.Articles['item'][1]['Url'] == 'http://ar2'

        
    
    msg = Article()
    msg.add_article("test", description="test", url="http://ar", image_url="http://img")
    msg.add_article("test2", description="test2", url="http://ar2", image_url="http://img2")
    
    msg.postmark(from_msg)
    msg = WeixinMsg(msg.xml)
    assert_msg(msg)

    msg = Article(articles=[
        {
            "Title": "test",
            "Description": "test",
            "PicUrl": "http://img",
            "Url": "http://ar"
        },
        {
            "Title": "test2",
            "Description": "test2",
            "PicUrl": "http://img2",
            "Url": "http://ar2"
        }
    ])
    
    msg.postmark(from_msg)
    msg = WeixinMsg(msg.xml)
    assert_msg(msg)

