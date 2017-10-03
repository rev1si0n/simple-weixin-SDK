# encoding=utf-8
from .utils import get_timestamp


def _make_node (k, v):
    if v : return "<{node}><![CDATA[{value}]]></{node}>".format(node=k, value=v)
    # 空字符串
    return ""


class _WeixinReply_ (dict):

    def __init__(self, from_msg):
        self['ToUserName'] = from_msg.FromUserName
        self['FromUserName'] = from_msg.ToUserName
        self['CreateTime'] = int(get_timestamp())


class TextReply(_WeixinReply_):

    def __init__(self, from_msg, content):

        super(TextReply, self).__init__ (from_msg)
        self['Content'] = content

        xmlform = \
        "<xml>"\
            "<ToUserName><![CDATA[{ToUserName}]]></ToUserName>"\
            "<FromUserName><![CDATA[{FromUserName}]]></FromUserName>"\
            "<CreateTime>{CreateTime}</CreateTime>"\
            "<MsgType><![CDATA[text]]></MsgType>"\
            "<Content><![CDATA[{Content}]]></Content>"\
        "</xml>"

        self.xml = xmlform.format(**self)


class ImageReply(_WeixinReply_):

    def __init__(self, from_msg, imageMediaId):
        super(ImageReply, self).__init__(from_msg)
        self['MediaId'] = mediaId

        xmlform = \
        "<xml>"\
            "<ToUserName><![CDATA[{ToUserName}]]></ToUserName>"\
            "<FromUserName><![CDATA[{FromUserName}]]></FromUserName>"\
            "<CreateTime>{CreateTime}</CreateTime>"\
            "<MsgType><![CDATA[image]]></MsgType>"\
            "<Image>"\
                "<MediaId><![CDATA[{MediaId}]]></MediaId>"\
            "</Image>"\
        "</xml>"

        self.xml = xmlform.format(**self)


class VoiceReply(_WeixinReply_):

    def __init__(self, from_msg, voiceMediaId):

        super(VoiceReply, self).__init__(from_msg)
        self['MediaId'] = mediaId

        xmlform = \
        "<xml>"\
            "<ToUserName><![CDATA[{ToUserName}]]></ToUserName>"\
            "<FromUserName><![CDATA[{FromUserName}]]></FromUserName>"\
            "<CreateTime>{CreateTime}</CreateTime>"\
            "<MsgType><![CDATA[voice]]></MsgType>"\
            "<Voice>"\
                "<MediaId><![CDATA[{MediaId}]]></MediaId>"\
            "</Voice>"\
        "</xml>"

        self.xml = xmlform.format(**self)


class VideoReply(_WeixinReply_):

    def __init__(self, from_msg, videoMediaId, title=None, description=None):

        super(VideoReply, self).__init__ (from_msg)
        self['MediaId'] = mediaId
        self['TitleNode'] = _make_node ("Title", title)
        self['DescriptionNode'] = _make_node ("Description", description)

        xmlform = \
        "<xml>"\
            "<ToUserName><![CDATA[{ToUserName}]]></ToUserName>"\
            "<FromUserName><![CDATA[{FromUserName}]]></FromUserName>"\
            "<CreateTime>{CreateTime}</CreateTime>"\
            "<MsgType><![CDATA[video]]></MsgType>"\
            "<Video>"\
                "<MediaId><![CDATA[{MediaId}]]></MediaId>"\
                "{TitleNode}{DescriptionNode}"\
            "</Video>"\
        "</xml>"\

        self.xml = xmlform.format(**self)


class MusicReply(_WeixinReply_):

    def __init__(self, from_msg, thumbMediaId, musicUrl=None, hqMusicUrl=None,  title=None, description=None):

        super(MusicReply, self).__init__(from_msg)
        self['ThumbMediaId'] = thumbMediaId
        self['TitleNode'] = _make_node ("Title", title)
        self['DescriptionNode'] = _make_node ("Description", description)
        self['MusicUrlNode'] = _make_node ("MusicUrl", musicUrl)
        self['HQMusicUrlNode'] = _make_node ("HQMusicUrl", hqMusicUrl)

        xmlform = \
        "<xml>"\
            "<ToUserName><![CDATA[{ToUserName}]]></ToUserName>"\
            "<FromUserName><![CDATA[{FromUserName}]]></FromUserName>"\
            "<CreateTime>{CreateTime}</CreateTime>"\
            "<MsgType><![CDATA[music]]></MsgType>"\
            "<Music>"\
                "{TitleNode}{DescriptionNode}{MusicUrlNode}{HQMusicUrlNode}"\
                "<ThumbMediaId><![CDATA[{ThumbMediaId}]]></ThumbMediaId>"\
            "</Music>"\
        "</xml>"

        self.xml = xmlform.format(**self)


class ArticleReply(_WeixinReply_):

    def __init__(self, from_msg, articles=[]):

        def make_item(articles):
            item = \
            "<item>"\
                "<Title><![CDATA[{Title}]]></Title>"\
                "<Description><![CDATA[{Description}]]></Description>"\
                "<PicUrl><![CDATA[{PicUrl}]]></PicUrl>"\
                "<Url><![CDATA[{Url}]]></Url>"\
            "</item>"

            def set_default(article):
                article.setdefault("Description", "")
                article.setdefault("PicUrl", "")
                article.setdefault("Url", "")

                return article

            return "".join (item.format(**set_default(_)) for _ in articles)

        super(ArticleReply, self).__init__(from_msg)
        self['Articles'] = make_item(articles)
        self['Count'] = len (articles)

        xmlform = \
        "<xml>"\
            "<ToUserName><![CDATA[{ToUserName}]]></ToUserName>"\
            "<FromUserName><![CDATA[{FromUserName}]]></FromUserName>"\
            "<CreateTime>{CreateTime}</CreateTime>"\
            "<MsgType><![CDATA[news]]></MsgType>"\
            "<ArticleCount>{Count}</ArticleCount>"\
            "<Articles>{Articles}</Articles>"\
        "</xml>"

        self.xml = xmlform.format(**self)


class EncryptReply(dict):

    def __init__(self, enctext, nonce, timestamp, signature):
        self['Encrypt'] = enctext
        self['Nonce'] = nonce
        self['TimeStamp'] = timestamp
        self['MsgSignature'] = signature

        xmlform = \
        "<xml>"\
            "<Encrypt><![CDATA[{Encrypt}]]></Encrypt>"\
            "<MsgSignature><![CDATA[{MsgSignature}]]></MsgSignature>"\
            "<TimeStamp>{TimeStamp}</TimeStamp>"\
            "<Nonce><![CDATA[{Nonce}]]></Nonce>"\
        "</xml>"

        self.xml = xmlform.format(**self)



class CustomMsgReply(object):

    @staticmethod
    def text(openid, content):
        return {
            "touser": openid,
            "msgtype": "text",
            "text": {
                "content": content
            }
        }

    @staticmethod
    def image(openid, mediaId):
        return {
            "touser": openid,
            "msgtype": "image",
            "image": {
                "media_id": mediaId
            }
        }

    @staticmethod
    def voice(openid, mediaId):
        return  {
            "touser": openid,
            "msgtype": "voice",
            "voice": {
                  "media_id": mediaId
            }
        }

    @staticmethod
    def video(openid, mediaId, thumbMediaId=None, title=None, desc=None):
        return {
            "touser": openid,
            "msgtype": "video",
            "video": {
                "media_id": mediaId,
                "thumb_media_id": thumbMediaId,
                "title": title,
                "description": desc
            }
        }

    @staticmethod
    def music(openid, musicUrl, hqMusicUrl, thumbMediaId, title=None, desc=None):
        return {
            "touser": openid,
            "msgtype": "music",
            "music": {
                "title": title,
                "description": desc,
                "musicurl": musicUrl,
                "hqmusicurl": hqMusicUrl,
                "thumb_media_id": thumbMediaId
            }
        }

    @staticmethod
    def article(openid, articles):
        return {
            "touser": openid,
            "msgtype": "news",
            "news": {
                "articles": articles
            }
        }

Text = TextReply
Image = ImageReply
Voice = VoiceReply
Video = VideoReply
Music = MusicReply
Article = ArticleReply
Encrypt = EncryptReply
CustomMsg = CustomMsgReply
