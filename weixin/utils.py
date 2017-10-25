# encoding=utf-8
import re
import hashlib
import time as _time
from random import choice


def get_timestamp():
    '''
    获取当前时间戳
    '''
    return _time.time()


def make_link(title, link):
    '''
    生成微信消息超链接的a标签
    '''
    h_tag = '<a href="%s">%s</a>' % (link, title)
    return h_tag


def binarify(s, encoding="utf-8"):
    '''
    将字符串，数字转化为bytes对象，同时也接受
    bytes对象，但是直接返回
    '''
    if isinstance(s, bytes):
        return s

    if isinstance(s, (int, float)):
        s = str(s)

    content = s.encode(encoding)
    return content


def stringify(s, encoding="utf-8"):
    '''
    将字节对象，数字转换为字符串str类型，同时也接收本来就是字符串
    str的类型，但是直接返回
    '''
    if isinstance(s, str):
        return s

    if isinstance(s, (int, float)):
        return str(s)

    content = s.decode(encoding)
    return content


def mix_seq(seq, type_=bytes):
    '''
    "".join(...)的函数式，因为我并不喜欢代码中出现太多的这种格式。
    所以写此作为代替。接收list与tuple类型的序列，type_代表序列中元素的类型。
    '''
    joiner = ("", b"")[type_ is bytes]
    return joiner.join(seq)


def get_nonce(length):
    '''
    返回一个随机字符串，length 代表随机字符串长度。
    '''
    table = '0123456789'\
            'abcdefghijklmnopqrstuvwxyz'\
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    seq = map(lambda x: choice(table), range(length))
    return mix_seq(seq, str)


def get_signature(*args):
    '''
    获取给定不定量参数的sha1 signature，参数可以同时是str/bytes
    '''
    args = sorted(map(binarify, args))
    sha1 = hashlib.sha1(mix_seq(args, bytes))

    return sha1.hexdigest()


def is_valid_request(token, nonce, timestamp, signature):
    """
    检查请求是否符合要求
    即查询字符串包含 nonce,timestamp,signature 且通过校验
    """
    sig = get_signature(token, nonce, timestamp)

    return sig == signature


def parse_rfc1738_args(url):
    """
    解析数据库url,
    正则表达式来自 sqlalchemy.
    """
    pattern = re.compile(r'''
            (?P<name>[\w\+]+)://
            (?:
                (?P<user>[^:/]*)
                (?::(?P<password>.*))?
            @)?
            (?:
                (?:
                    \[(?P<ipv6host>[^/]+)\] |
                    (?P<ipv4host>[^/:]+)
                )?
                (?::(?P<port>[^/]*))?
            )?
            (?:/(?P<database>.*))?
            ''', re.X)

    m = pattern.match(url)
    if m is None:
        return

    components = m.groupdict()
    components['host'] = components['ipv4host'] \
                         or components['ipv6host']

    del components['ipv6host']
    del components['ipv4host']
    return components


class AttributeDictError(Exception):
    pass


class AttributeDict(dict):
    """
    增加属性访问的字典, 仅支持单层字典的属性访问
    """

    def __getattr__(self, key):
        """
        提供属性访问方法
        如果属性在字典中不存在, 返回 None
        """
        try:
            # 尝试读取字典key
            return super(AttributeDict, self).__getitem__(key)
        except KeyError:
            return

    def __getitem__(self, key):
        """
        普通字典方式访问
        如果key不存在也不会抛出KeyError
        """
        try:
            return super(AttributeDict, self).__getitem__(key)
        except KeyError:
            pass

    def set(self, key, value):
        """
        设置一个属性
        多次设置相同属性会覆盖, 且无提示
        """
        if key.startswith("__") and key.endswith("__"):
            raise AttributeDictError(
                "name type __[name]__ is reserved."
            )

        super(AttributeDict, self).__setitem__(key, value)

    __setattr__ = set

    def setnx(self, key, value):
        """
        仅当属性不存在时设置属性
        setnx = set when not exist
        """

        if not self.__getitem__(key):
            self.set(key, value)

    def remove(self, key):
        """
        删除一个key/属性
        不论是否存在key, 无返回值
        """
        try:
            self.__delitem__(key)
        except KeyError:
            pass


class _NULL_(AttributeDict):
    """
    替代 None 对象
    这样即使访问到了未提供的属性或是key也不会抛出 AttributeError/ KeyError
    """

    def __bool__(self):
        return not 1


__all__ = ['get_timestamp',
           'make_link',
           'binarify',
           'mix_seq',
           'get_nonce',
           'get_signature',
           'is_valid_request',
           'AttributeDict',
           '_NULL_']
