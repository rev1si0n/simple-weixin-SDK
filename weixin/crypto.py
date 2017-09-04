# encoding=utf-8
import base64
from Crypto.Cipher import AES

from .utils import (
    get_timestamp,
    mix_seq,
    binarify,
    stringify,
    get_signature,
    get_nonce)


def base64_encode(s, encoding="utf-8"):
    """
    简写的base64编码
    """
    s = binarify(s, encoding=encoding)
    data = base64.b64encode(s)
    return data


def base64_decode(s):
    """
    简写的base64解码
    """
    data = base64.b64decode(s)
    return data


class CryptorError(Exception):
    """
    CryptorError
    """
    pass


class AESCipher:
    """
    基础部分来自 http://stackoverflow.com/questions/12524994
    稍微做了一下兼容性修改
    """
    
    def __init__(self, key):
        self.BS = 32

        def pad(s):
            lenth = (self.BS - len(s) % self.BS)
            chr_ = chr(lenth)
            if isinstance(s, bytes):
                chr_ = binarify(chr_)

            return s + (lenth * chr_)

        self.key = key
        self.pad = pad
        self.unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    def encrypt(self, raw):
        raw = self.pad(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, self.key[:16])
        return base64_encode(cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64_decode(enc)
        cipher = AES.new(self.key, AES.MODE_CBC, self.key[:16])
        return self.unpad(cipher.decrypt(enc))


class XMLMsgCryptor(object):
    """
    微信消息加解密类
    """
    def __init__(self, appid, token, enc_aeskey):
        """
        初始化时提供 appid, token, enc_aeskey
        此类正常情况下用户无需接触
        """
        pad = ("=" * (len(enc_aeskey) % 3))
        aeskey = base64_decode(enc_aeskey + pad)

        self.token = token
        self.appid = appid.encode('ascii')
        self.cryptor = AESCipher(aeskey)

    def decrypt(self, enctext, appid_check=True):
        """
        解密消息
        """
        text = self.cryptor.decrypt(enctext)
        # xml 内容的长度
        lenth = int.from_bytes(text[16:20], 'big')
        if appid_check :
            # appid 检查，如果解密出来的appid与提供的不同，那么返回 None
            aid = text[lenth + 20:]
            if aid != self.appid:
                """
                解密消息中的appid不等于提供的appid, 触发异常
                """
                raise CryptorError(
                    "message appid %s not equ %s" % (aid, self.appid))

        # 返回xml
        content = stringify(text[20: lenth + 20])
        return content

    def encrypt(self, xml):
        """
        加密消息, xml 为已经渲染好的原始xml
        """
        
        # 先将xml转换为字节，否则当内容含有多字节字符时会导致len计数错误
        xml = binarify(xml)

        blenth = int.to_bytes(len(xml), 4, 'big')

        seq = mix_seq(map(binarify, [get_nonce(16), blenth, xml, self.appid]), bytes)
        enctext = self.cryptor.encrypt(seq)
        enctext = stringify(enctext)

        # 加密后的内容, bytes Type
        nonce = get_nonce(5)
        timestamp = get_timestamp()

        sig = get_signature(self.token, nonce, timestamp, enctext)

        # 返回的字典供 reply.EncryptReply 使用
        return dict(enctext=enctext,
                    nonce=nonce,
                    timestamp=timestamp,
                    signature=sig)


__all__ = ["AESCipher",
           "XMLMsgCryptor",
           "CryptorError",
           "base64_encode",
           "base64_decode"]
