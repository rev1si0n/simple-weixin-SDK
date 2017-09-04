# encoding=utf-8
import re
import IPy
import requests
from json import dumps, loads

from .utils import binarify


class ClientError(Exception):
    pass


class Client(object):

    def __init__(self, config):
        """
        config: config.Config 类
        """
        self.config = config

        # 设置默认的api服务器地址
        self.config.setnx("domain", "api.weixin.qq.com")

    def get_api_base(self, protocol="https"):
        """
        其实这个本来是没必要的
        但是看到文档说视频文件不支持https下载的时候就慌了, 所以改了一下
        然后...发现好像真蠢，原来仅一厘米之隔的下面说明了：
        当素材为视频，返回的是url!!!woc
        """

        return "".join([protocol, "://", self.config.domain])

    def get_access_token_from_db(self):
        """
        从全局配置的数据存储器获取ACCESS_TOKEN
        """
        storage = self.config.storage
        token = storage.get("weixin:ACCESS_TOKEN", encoding="utf-8")
        return token

    def refresh_access_token(self, expires=None):
        """
        刷新access_token, 并将其保存到全局的数据存储器当中
        须保证只有一个进/线程可以访问访问此方法, 默认的过期时间原始expires_in
        应该定时调用此方法
        """
        result = self.get_access_token()

        token = result["access_token"]
        exp = expires or result['expires_in']

        storage = self.config.storage
        storage.set("weixin:ACCESS_TOKEN", token, expires=exp)
        return token

    def _read_file(self, file):
        """
        从本地/网络读取文件
        file: 可以是http/s协议的网络文件或者本地文件路径
        """
        if re.match("^https?://", file):
            # 下载图片, 稍微伪装一下UA
            hd = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(file, headers=hd)

            content = resp.content

        else:
            content = open(file, 'rb').read()

        return content

    def get_media_type_by_file_suffix(self, filename):
        """
        通过文件/网络文件的后缀名判断媒体类型
        需要注意如果是网络文件则必须要去掉url中的任何参数
        有些网络文件由于没有后缀名如微信头像url，所以无法判断
        """
        match = re.search("\.(?P<suffix>PNG|JPEG|JPG|GIF|AMR|MP3|MP4)$",
                          filename,
                          re.IGNORECASE)

        if not match:
            return

        suffix = match.group("suffix").upper()

        if suffix in "PNG\JPEG\JPG\GIF":
            return "image"

        elif suffix in "AMR\MP3":
            return "voice"

        return "video"

    def make_request(self, path, method=None,
                     params={},
                     data=None,
                     with_token=False,
                     raw_response=False, **kwargs
                     ):
        """
        所有对微信服务器的请求都会经过这里
        path: 请求路径
        method: 请求方法
        params: GET参数
        data: POST的body, 在这里data必须是字典或者列表类型
        with_token: 是否在GET参数中加上access_token
        kwargs: 其他传给requests的参数
        """
        if with_token:
            # 如果请求需要token则在get参数中带上token
            token = self.get_access_token_from_db()
            if token is None:
                raise ClientError(
                    "no access token in database!")

            params["access_token"] = token

        if data is not None:

            # data必须是字典或者列表类型
            data = dumps(data, ensure_ascii=False)
            data = binarify(data)

        resp = requests.request(url=self.get_api_base() + path,
                    method=method,
                    params=params,
                    data=data,
                    **kwargs
                    )

        if raw_response:
            return resp

        result = loads(resp.content.decode("utf-8"))
        # 对返回数据进行简单检查, 是否请求失败
        code = result.get("errcode", 0)
        if code is not 0:

            # 微信api返回了错误码, 触发异常
            param = (code, result.get("errmsg"))
            raise ClientError(
                "api returned error, code=%s, msg=%s." % param)

        return result

    def get_access_token(self):
        """
        向微信服务器请求一个新的access_token
        """
        return self.make_request(
            "/cgi-bin/token",
            method="GET",
            params=dict(
                grant_type="client_credential",
                appid=self.config.appid,
                secret=self.config.appsec
                )
            )

    def get_user_info(self, openid, lang="zh_CN"):
        """
        向微信服务器请求一个用户的基本信息
        openid: 用户openid
        lang: 参见微信文档
        """
        return self.make_request(
            "/cgi-bin/user/info",
            method="GET",
            params=dict(openid=openid, lang=lang),
            with_token=True
            )

    def get_ip_list(self, parse_subnet=False):
        """
        获取微信服务器的ip地址列表
        parse_subnet: 如果设置为True, 将会返回子网中的所有ip
        """

        result = self.make_request(
            "/cgi-bin/getcallbackip",
            method="GET",
            with_token=True
            )

        ip_list = result["ip_list"]
        if parse_subnet:
            sub_ip_list = []
            for ip in map(IPy.IP, ip_list):
                mmp = map(lambda x: str(x), ip)
                sub_ip_list.extend(mmp)

            return sub_ip_list

        return ip_list

    def create_menu(self, menu):
        """
        创建自定义菜单
        menu: 参见微信开发者文档
        """
        return self.make_request(
            "/cgi-bin/menu/create",
            method="POST",
            data=menu,
            with_token=True
            )

    def get_menu(self):
        """
        获取当前的菜单设置
        将会直接返回响应内容的menu结点
        """
        result = self.make_request(
            "/cgi-bin/menu/get",
            method="GET",
            with_token=True
            )

        return result["menu"]

    def delete_menu(self):
        """
        删除自定义菜单
        """
        return self.make_request(
            "/cgi-bin/menu/delete",
            method="GET",
            with_token=True
            )

    def create_kfaccount(self, kf_account, nickname, passwd):
        """
        创建客服
        kf_account, nickname, passwd: 参见微信开发者文档
        """
        return self.make_request(
            "/customservice/kfaccount/add",
            method="POST",
            with_token=True,
            data=dict(
                kf_account=kf_account,
                nickname=nickname,
                password=passwd
                )
            )

    def update_kfaccount(self, kf_account, nickname, passwd):
        """
        修改客服信息
        kf_account, nickname, passwd: 参见微信开发者文档
        """
        return self.make_request(
            "/customservice/kfaccount/update",
            method="POST",
            with_token=True,
            data=dict(
                kf_account=kf_account,
                nickname=nickname,
                password=passwd
                )
            )

    def delete_kfaccount(self, kf_account, nickname, passwd):
        """
        删除客服
        kf_account, nickname, passwd: 参见微信开发者文档
        """
        return self.make_request(
            "/customservice/kfaccount/del",
            method="POST",
            with_token=True,
            data=dict(
                kf_account=kf_account,
                nickname=nickname,
                password=passwd
                )
            )

    def upload_kfavatar(self, kf_account, avatar):
        """
        设置客服头像
        kf_account: 参见微信开发者文档
        avatar: 可以是本地文件也可以是http/s协议的网络文件,
                按照要求, 必须是jpg文件
        """
        content = self._read_file(avatar)

        return self.make_request(
            "/customservice/kfaccount/uploadheadimg",
            method="POST",
            params=dict(kf_account=kf_account),
            files={"file": (avatar, content)},
            with_token=True
            )

    def get_kflist(self):
        """
        获取客服列表
        """
        return self.make_request(
            "/cgi-bin/customservice/getkflist",
            method="GET",
            with_token=True
            )

    def send_custom_message(self, message):
        """
        发送客服消息/基础
        message: 参见客服消息类型/json
        """
        return self.make_request(
            "/cgi-bin/message/custom/send",
            method="POST",
            with_token=True,
            data=message
            )

    def upload_tmp_media(self, media, media_type=None):
        """
        上传临时素材
        media: 本地文件/网络文件
        media_type: 为None时会根据文件后缀名自动判断
        """
        if media_type is None:
            media_type = self.get_media_type_by_file_suffix(media)

            # 无法获取媒体类型且用户未指定, 无法继续愉快玩耍
            if not media_type:
                raise ClientError(
                    "cannot guess mediatype from %s." % media)

        content = self._read_file(media)

        return self.make_request(
            "/cgi-bin/media/upload",
            method="POST",
            params=dict(type=media_type),
            files={"file": (media, content)},
            with_token=True
            )

    def download_tmp_media(self, media_id):
        """
        下载媒体文件
        media_id: 熊猫摸头
        由于响应头中包含媒体类型且当媒体类型是视频返回的是json url所以这里需要自己处理
        参见：https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1444738727
        """
        return self.make_request(
            "/cgi-bin/media/get",
            method="GET",
            params=dict(media_id=media_id),
            raw_response=True,
            with_token=True
            )

__all__ = ["Client", "ClientError"]
