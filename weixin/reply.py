# encoding=utf-8
from .utils import get_timestamp


def CDATA_escape(escape_s):
    """
    转义xml的CDATA中的]]>
    偶然在一次测试下发现当CDATA中包含</xml>结束标签时也会导致微信非正常解析
    即如果CDATA内容为 <![CDATA[你😫</xml>(⊙﹏⊙)]]>，用户收到的内容却为
    你😫</root>, 且此结束标签只在全小写状态下会导致这种情况。
    """
    if escape_s is not None:
        escape_s = escape_s.replace("]]>", ']]&gt;')
        escape_s = escape_s.replace("</xml>", '</xml&gt;')
        return escape_s


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
        self['Content'] = CDATA_escape(content)

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

        title = CDATA_escape(title)
        description = CDATA_escape(description)

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

        title = CDATA_escape(title)
        description = CDATA_escape(description)

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

                a_title = article['Title']
                a_desc = article['Description']

                article['Title'] = CDATA_escape(a_title)
                article['Description'] = CDATA_escape(a_desc)

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
