# encoding=utf-8
import re
import IPy
import requests
from json import dumps, loads

from .utils import to_bytes


__all__ = ["Client", "ClientError"]


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
        return "".join([protocol, "://", self.config.domain])

    def get_access_token_from_db(self):
        storage = self.config.storage
        token = storage.get("weixin:ACCESS_TOKEN", encoding="utf-8")
        return token

    def refresh_access_token(self, expires=None):
        result = self.get_access_token()

        token = result["access_token"]
        exp = expires or result['expires_in']

        storage = self.config.storage
        storage.set("weixin:ACCESS_TOKEN", token, expires=exp)
        return token

    def _read_file(self, file):
        if re.match("^https?://", file):
            # 文件是url, 下载图片, 稍微伪装一下UA
            resp = requests.get(file, headers={"User-Agent": "Mozilla/5.0"})
            content = resp.content

        else:
            # 从本地文件读取
            content = open(file, 'rb').read()

        return content

    def _format_json(self, data):
        return dumps(data, indent=4, ensure_ascii=False)

    def get_media_type_by_file_suffix(self, filename):
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

    def make_request(self, path, method=None, params=None, data=None, with_token=False, raw_response=False, **kwargs):
        params = params or {}
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
            data = to_bytes(data)

        resp = requests.request(
            url=self.get_api_base() + path,
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
        if code != 0:
            # 微信api返回了错误码, 触发异常
            raise ClientError(
                "api returned error, code=%s, msg=%s." % (code, result.get("errmsg")))

        return result

    def get_access_token(self):
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
        return self.make_request(
            "/cgi-bin/user/info",
            method="GET",
            params=dict(openid=openid, lang=lang),
            with_token=True
            )

    def get_ip_list(self, parse_subnet=False):
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
        return self.make_request(
            "/cgi-bin/menu/create",
            method="POST",
            data=menu,
            with_token=True
            )

    def get_menu(self, string=False):
        result = self.make_request(
            "/cgi-bin/menu/get",
            method="GET",
            with_token=True
            )

        menu = result["menu"]
        if not string:
            return menu

        return self._format_json(menu)

    def delete_menu(self):
        return self.make_request(
            "/cgi-bin/menu/delete",
            method="GET",
            with_token=True
            )

    def create_kfaccount(self, kf_account, nickname, passwd):
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
        content = self._read_file(avatar)
        return self.make_request(
            "/customservice/kfaccount/uploadheadimg",
            method="POST",
            params=dict(kf_account=kf_account),
            files={"file": (avatar, content)},
            with_token=True
            )

    def get_kflist(self):
        return self.make_request(
            "/cgi-bin/customservice/getkflist",
            method="GET",
            with_token=True
            )

    def send_custom_message(self, message):
        return self.make_request(
            "/cgi-bin/message/custom/send",
            method="POST",
            with_token=True,
            data=message
            )

    def upload_tmp_media(self, media, media_type=None):
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
        return self.make_request(
            "/cgi-bin/media/get",
            method="GET",
            params=dict(media_id=media_id),
            raw_response=True,
            with_token=True
            )
