# encoding=utf-8
import xmltodict

from .reply import EncryptReply
from .utils import get_timestamp, AttributeDict


class WeixinMsg(AttributeDict):

    def __init__(self, xmlstr):
        """
        解析XML消息为AttributeDict
        """
        
        super(WeixinMsg, self).__init__(xmltodict.parse(xmlstr)['xml'])
