# encoding=utf-8
import xmltodict

from .utils import get_timestamp, AttributeDict


class WeixinMsg(AttributeDict):

    def __init__(self, xmlstr):
        super(WeixinMsg, self).__init__(xmltodict.parse(xmlstr)['xml'])
