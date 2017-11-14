# encoding=utf-8
from xml.parsers.expat import ExpatError

from .utils import AttrNone
from .session import Session
from .parse import WeixinMsg
from .reply import EncryptReply


class WeixinRequest(object):
    """
    微信请求
    此类即发送给用户handler的唯一参数
    相当于django view 的参数request, 或者 Tornado Handler 的 web.RequestHandler
    该类在 /wechatter.Weechat.reply 中被使用
    提供了会话支持, 以及一个xml渲染方法
    """

    def __init__(self, config, xmldoc):
        """
        config 应用的设置
        xmldoc 是微信POST来的XML体
        """
        self.config = config
        self._raw_xml_ = xmldoc
        self._response_xml_ = None

    @property
    def session(self):
        """
        首次访问session属性时获取会话信息。
        """
        if not hasattr(self, '_weixin_session_'):
            self._weixin_session_ = Session(self)

        return self._weixin_session_

    @property
    def message(self):
        """
        首次访问message属性时解析微信消息。
        """
        if not hasattr(self, '_weixin_msg_'):
            self._weixin_msg_ = AttrNone()
            if self._raw_xml_:
                try:
                    self._weixin_msg_ = WeixinMsg(self._raw_xml_)
                    encrypted_msg = self._weixin_msg_.Encrypt
                    cryptor = self.config.cryptor

                    if encrypted_msg and cryptor:
                        # 解密被加密的消息Encrypt
                        body = cryptor.decrypt(encrypted_msg)

                        del self._weixin_msg_
                        self._weixin_msg_ = WeixinMsg(body)

                    elif encrypted_msg or cryptor:
                        raise Exception(
                            "message {0}encrypted but enc_aeskey is {1}set.".format(
                            "" if encrypted_msg else "not ",
                            "" if cryptor else "not ",
                            )
                        )

                except (ExpatError, KeyError):
                    # 非正常xml文本或者xml格式不符合要求
                    raise

        return self._weixin_msg_

    def response(self, template, *args, **kwargs):
        """
        使用模板渲染出xml, 模板来自 relpy.*, 会自动根据
        是否设定了cryptor来判断是否需要将消息加密
        """
        t = template(self.message, *args, **kwargs)
        if self.config.cryptor:
            # 设置了消息加解密, 加密明文消息
            kw = self.config.cryptor.encrypt(t.xml)
            t = EncryptReply(**kw)

        self._response_xml_ = t.xml
        return

    def get_response_xml(self, default=None):
        """
        获取响应的xml文档
        """
        return self._response_xml_ or default
