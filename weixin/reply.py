# encoding=utf-8
from .utils import get_timestamp, join_sequence


def cdata_escape(escape_s):
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


def _make_node(k, v):
    if v : return "<{node}><![CDATA[{value}]]></{node}>".format(node=k, value=v)
    # 空字符串
    return ""


class BaseWeixinReply(dict):

    def __init__(self):
        self._marked = False

    def postmark(self, from_msg, created=None):
        self['ToUserName'] = from_msg.FromUserName
        self['FromUserName'] = from_msg.ToUserName
        self['CreateTime'] = created or int(get_timestamp())
        self._marked = True

    def _generate(self):
        raise NotImplementedError

    @property
    def xml(self):
        # generate xml
        return self._generate()


class TextReply(BaseWeixinReply):

    def __init__(self, content):
        super(TextReply, self).__init__()

        self['Content'] = cdata_escape(content)

    def _generate(self):
        template = \
            "<xml>" \
            "<ToUserName><![CDATA[{ToUserName}]]></ToUserName>" \
            "<FromUserName><![CDATA[{FromUserName}]]></FromUserName>" \
            "<CreateTime>{CreateTime}</CreateTime>" \
            "<MsgType><![CDATA[text]]></MsgType>" \
            "<Content><![CDATA[{Content}]]></Content>" \
            "</xml>"

        return template.format(**self)


class ImageReply(BaseWeixinReply):

    def __init__(self, media_id):
        super(TextReply, self).__init__()

        self['MediaId'] = media_id

    def _generate(self):
        template = \
            "<xml>" \
            "<ToUserName><![CDATA[{ToUserName}]]></ToUserName>" \
            "<FromUserName><![CDATA[{FromUserName}]]></FromUserName>" \
            "<CreateTime>{CreateTime}</CreateTime>" \
            "<MsgType><![CDATA[image]]></MsgType>" \
            "<Image>" \
            "<MediaId><![CDATA[{MediaId}]]></MediaId>" \
            "</Image>" \
            "</xml>"

        return template.format(**self)


class VoiceReply(BaseWeixinReply):

    def __init__(self, media_id):
        super(TextReply, self).__init__()

        self['MediaId'] = media_id

    def _generate(self):
        template = \
            "<xml>" \
            "<ToUserName><![CDATA[{ToUserName}]]></ToUserName>" \
            "<FromUserName><![CDATA[{FromUserName}]]></FromUserName>" \
            "<CreateTime>{CreateTime}</CreateTime>" \
            "<MsgType><![CDATA[voice]]></MsgType>" \
            "<Voice>" \
            "<MediaId><![CDATA[{MediaId}]]></MediaId>" \
            "</Voice>" \
            "</xml>"

        return template.format(**self)


class VideoReply(BaseWeixinReply):

    def __init__(self, media_id, title=None, description=None):
        super(TextReply, self).__init__()

        title = cdata_escape(title)
        description = cdata_escape(description)

        self['MediaId'] = media_id
        self['TitleNode'] = _make_node("Title", title)
        self['DescriptionNode'] = _make_node("Description", description)

    def _generate(self):
        template = \
            "<xml>" \
            "<ToUserName><![CDATA[{ToUserName}]]></ToUserName>" \
            "<FromUserName><![CDATA[{FromUserName}]]></FromUserName>" \
            "<CreateTime>{CreateTime}</CreateTime>" \
            "<MsgType><![CDATA[video]]></MsgType>" \
            "<Video>" \
            "<MediaId><![CDATA[{MediaId}]]></MediaId>" \
            "{TitleNode}{DescriptionNode}" \
            "</Video>" \
            "</xml>"

        return template.format(**self)


class MusicReply(BaseWeixinReply):

    def __init__(self, thumb_media_id, url=None, hq_url=None,  title=None, description=None):
        super(TextReply, self).__init__()

        title = cdata_escape(title)
        description = cdata_escape(description)

        self['ThumbMediaId'] = thumb_media_id
        self['TitleNode'] = _make_node ("Title", title)
        self['DescriptionNode'] = _make_node ("Description", description)
        self['MusicUrlNode'] = _make_node ("MusicUrl", url)
        self['HQMusicUrlNode'] = _make_node ("HQMusicUrl", hq_url)

    def _generate(self):
        template = \
            "<xml>" \
            "<ToUserName><![CDATA[{ToUserName}]]></ToUserName>" \
            "<FromUserName><![CDATA[{FromUserName}]]></FromUserName>" \
            "<CreateTime>{CreateTime}</CreateTime>" \
            "<MsgType><![CDATA[music]]></MsgType>" \
            "<Music>" \
            "{TitleNode}{DescriptionNode}{MusicUrlNode}{HQMusicUrlNode}" \
            "<ThumbMediaId><![CDATA[{ThumbMediaId}]]></ThumbMediaId>" \
            "</Music>" \
            "</xml>"

        return template.format(**self)


class ArticleReply(BaseWeixinReply):

    def __init__(self, articles=None):
        super(TextReply, self).__init__()

        self.articles = articles or []

    def _generate(self):
        def make_item(articles):
            item = \
                "<item>" \
                "<Title><![CDATA[{Title}]]></Title>" \
                "<Description><![CDATA[{Description}]]></Description>" \
                "<PicUrl><![CDATA[{PicUrl}]]></PicUrl>" \
                "<Url><![CDATA[{Url}]]></Url>" \
                "</item>"

            def set_default(article):
                article.setdefault("Description", "")
                article.setdefault("PicUrl", "")
                article.setdefault("Url", "")

                a_title = article['Title']
                a_desc = article['Description']

                article['Title'] = cdata_escape(a_title)
                article['Description'] = cdata_escape(a_desc)

                return article

            return join_sequence(
                item.format(**set_default(ar)) for ar in articles
            )

        self['Articles'] = make_item(self.articles)
        self['Count'] = len(self.articles)

        template = \
            "<xml>" \
            "<ToUserName><![CDATA[{ToUserName}]]></ToUserName>" \
            "<FromUserName><![CDATA[{FromUserName}]]></FromUserName>" \
            "<CreateTime>{CreateTime}</CreateTime>" \
            "<MsgType><![CDATA[news]]></MsgType>" \
            "<ArticleCount>{Count}</ArticleCount>" \
            "<Articles>{Articles}</Articles>" \
            "</xml>"

        return template.format(**self)

    def add_article(self, title, description=None, url=None, image_url=None):
        ar = dict()

        ar['Title'] = title
        if url: ar['Url'] = url
        if image_url: ar['PicUrl'] = image_url
        if description: ar['Description'] = description

        self.articles.append(ar)


class EncryptReply(BaseWeixinReply):

    def __init__(self, enctext, nonce, timestamp, signature):
        super(TextReply, self).__init__()
        
        self['Encrypt'] = enctext
        self['Nonce'] = nonce
        self['TimeStamp'] = timestamp
        self['MsgSignature'] = signature

    def postmark(self, from_msg):
        self._marked = True

    def _generate(self):
        template = \
            "<xml>"\
            "<Encrypt><![CDATA[{Encrypt}]]></Encrypt>" \
            "<MsgSignature><![CDATA[{MsgSignature}]]></MsgSignature>" \
            "<TimeStamp>{TimeStamp}</TimeStamp>" \
            "<Nonce><![CDATA[{Nonce}]]></Nonce>" \
            "</xml>"

        return template.format(**self)


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
    def image(openid, media_id):
        return {
            "touser": openid,
            "msgtype": "image",
            "image": {
                "media_id": media_id
            }
        }

    @staticmethod
    def voice(openid, media_id):
        return  {
            "touser": openid,
            "msgtype": "voice",
            "voice": {
                  "media_id": media_id
            }
        }

    @staticmethod
    def video(openid, media_id, thumb_media_id=None, title=None, desc=None):
        return {
            "touser": openid,
            "msgtype": "video",
            "video": {
                "media_id": media_id,
                "thumb_media_id": thumb_media_id,
                "title": title,
                "description": desc
            }
        }

    @staticmethod
    def music(openid, url, hq_url, thumb_media_id, title=None, desc=None):
        return {
            "touser": openid,
            "msgtype": "music",
            "music": {
                "title": title,
                "description": desc,
                "musicurl": url,
                "hqmusicurl": hq_url,
                "thumb_media_id": thumb_media_id
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
