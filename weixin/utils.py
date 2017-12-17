# encoding=utf-8
import re
import hashlib
import json as _json
import time as _time
from random import choice


__all__ = [
    'get_timestamp',
    'make_link',
    'to_bytes',
    'binarify',
    'to_str',
    'stringify',
    'join_sequence',
    'mix_seq',
    'get_nonce',
    'get_signature',
    'is_valid_request',
    'AttributeDict',
    'AttrNone',
]


def get_timestamp():
    return _time.time()


def make_link(title, link):
    h_tag = '<a href="%s">%s</a>' % (link, title)
    return h_tag


def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        # default encoding 'utf-8'
        value = bytes_or_str.decode()
    elif isinstance(bytes_or_str, (int, float)):
        # translate int, float to string
        value = repr(bytes_or_str)
    else:
        value = bytes_or_str
    return value

stringify = to_str


def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, (str, int, float)):
        # default encoding 'utf-8'
        value = to_str(bytes_or_str).encode()
    else:
        value = bytes_or_str
    return value

binarify = to_bytes


def join_sequence(seq):
    seq = list(seq)
    return type(seq[0])().join(seq)

mix_seq = join_sequence


def get_nonce(length):
    table = '0123456789'\
            'abcdefghijklmnopqrstuvwxyz'\
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    seq = map(lambda x: choice(table), range(length))
    return join_sequence(seq)


def get_signature(*args):
    args = sorted(map(to_bytes, args))
    sha1 = hashlib.sha1(join_sequence(args))

    return sha1.hexdigest()


def is_valid_request(token, nonce, timestamp, signature):
    sig = get_signature(token, nonce, timestamp)
    return sig == signature


def parse_rfc1738_args(url):
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


class AttributeDict(dict):

    def __getattr__(self, key):
        try:
            # 尝试读取字典key
            return super(AttributeDict, self).__getitem__(key)
        except KeyError:
            pass

    def __getitem__(self, key):
        try:
            return super(AttributeDict, self).__getitem__(key)
        except KeyError:
            pass

    def set(self, key, value):
        super(AttributeDict, self).__setitem__(key, value)

    __setattr__ = set

    def setnx(self, key, value):
        if not self.__getitem__(key):
            self.set(key, value)

    def remove(self, key):
        try:
            self.__delitem__(key)
        except KeyError:
            pass


class AttrNone(AttributeDict):

    def __bool__(self):
        return not 1


def json_dumps(py_dict, **kwargs):
    kwargs.setdefault('ensure_ascii', False)
    return _json.dumps(py_dict, **kwargs)


def json_loads(json, **kwargs):
    return _json.loads(json, **kwargs)
