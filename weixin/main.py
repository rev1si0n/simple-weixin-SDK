# encoding=utf-8
import re

from .config import Config
from .crypto import XMLMsgCryptor
from .request import WeixinRequest
from .storage import Sqlite3Storage


class Weechat(object):

    def __init__(self, token=None, appid=None, appsec=None):
        """
        如果设置了enc_aeskey那么回复/接收消息都会调用解密过程
        """
        self.config = Config()

        # 存储token, appid, appsec
        self.add_config("token", token)
        self.add_config("appid", appid)
        self.add_config("appsec", appsec)

        default = lambda req: None

        self.handlers = dict()

        # 未知消息类型的处理器
        self.default = default

        # 关键字处理器数组
        self.text_filter_handlers = []
        # 默认关键字无匹配处理器
        self.text_filter_default = default

        # click事件处理器数组
        self.key_filter_handlers = dict()
        # 默认无匹配事件key的处理器
        self.key_filter_default = default

    def initialize(self):
        """
        初始化配置，此方法必须在make_handler中调用
        """
        appid = self.config.appid
        token = self.config.token
        enc_aeskey = self.config.enc_aeskey

        if not appid or not token:
            raise Exception("appid or token not set!")

        if enc_aeskey:
            ##
            # 设置了消息加解密密钥, 实例化一个消息cryptor
            ##
            self.add_config("cryptor", XMLMsgCryptor(
                    appid=appid,
                    token=token,
                    enc_aeskey=enc_aeskey
                )
            )

        if self.config.storage is None:
            ##
            # 未设置存储器, 设置默认sqlite3存储器, 文件以appid命名
            ##
            sqlite_file = "weixin.%s.sqlite3" % appid
            storage = Sqlite3Storage(uri=sqlite_file)
            self.set_storage(storage)

    def add_config(self, key, value):
        """
        添加全局设置

        可以添加全局参数, 在处理器中可以访问, 主要是省去了有些多个文件中需要导入某些
        如数据库连接的比较麻烦的方法

        !! 重复添加相同名称的属性会导致覆盖

        >>> @app.text_filter(["签到", ])
        >>> def sign(request):
        >>>     database = request.config.sqlconn
        >>>     result = database.execute("SELECT * FROM...
        >>>     ...
        >>>
        """
        self.config.set(key, value)

    def set_storage(self, storage):
        """
        设置全局的缓存存储器
        此存储器主要用来存储会话信息, 以及共享 access_token 等
        还可自用于key->value存储器
        """

        self.add_config("storage", storage)

    def add_base_handler(self, type_, function):
        """
        设置一个对应MsgType的处理器
        """
        type_ = self.uniform(type_)
        self.handlers[type_] = function
        return

    def get_base_handler(self, type_):
        """
        根据消息类型返回对应的处理器
        """
        type_ = self.uniform(type_)
        handler = self.handlers.get(type_, self.default)
        return handler

    def uniform(self, key):
        """
        将key转换为大写
        """
        return key.upper()

    def text(self, function):
        """
        装饰 MsgType=text （文本消息）的处理器
        """
        self.add_base_handler("text", function)
        return function

    def image(self, function):
        """
        装饰 MsgType=image（图片消息） 的处理器
        """
        self.add_base_handler("image", function)
        return function

    def voice(self, function):
        """
        装饰 MsgType=voice（语音消息) 的处理器
        """
        self.add_base_handler("voice", function)
        return function

    def video(self, function):
        """
        装饰 MsgType=video（视频消息） 的处理器
        """
        self.add_base_handler("video", function)
        return function

    def shortvideo(self, function):
        """
        装饰 MsgType=shortvideo（短视频消息） 的处理器
        """
        self.add_base_handler("shortvideo", function)
        return function

    def location(self, function):
        """
        装饰 MsgType=location（位置消息） 的处理器
        """
        self.add_base_handler("location", function)
        return function

    def link(self, function):
        """
        装饰 MsgType=text 的处理器
        """
        self.add_base_handler("link", function)
        return function

    def subscribe_event(self, function):
        """
        装饰 MsgType=event, Event=subscribe 的处理器
        用户刚刚关注时调用
        """
        self.add_base_handler("event_subscribe", function)
        return function

    def unsubscribe_event(self, function):
        """
        装饰 MsgType=event, Event=unsubscribe 的处理器
        用户取消关注时调用
        """
        self.add_base_handler("event_unsubscribe", function)
        return function

    def location_event(self, function):
        """
        装饰 MsgType=event, Event=location 的处理器
        上报地理位置事件
        """
        self.add_base_handler("event_location", function)
        return function

    def click_event(self, function):
        """
        装饰 MsgType=event, Event=click 的处理器
        自定义菜单click事件
        """
        self.add_base_handler("event_click", function)
        return function

    def view_event(self, function):
        """
        装饰 MsgType=event, Event=view 的处理器
        点击菜单跳转链接时的事件推送
        """
        self.add_base_handler("event_view", function)
        return function

    def click_event_filter(self, key):
        """
        为click事件的一个eventkey绑定一个处理器
        需要注意, 此装饰器请勿与self.click_event同时使用, 因为此装饰器会注册
        一个处理click事件的eventkey路由器
        """

        def __wrapper__(function):
            # 注册key处理器
            self.key_filter_handlers[key] = function

            # 注册key路由器
            @self.click_event
            def handle_click_event(weixin):
                # 获取click的eventkey
                key = weixin.message.EventKey
                handler = self.key_filter_handlers.get(
                    key,
                    self.key_filter_default
                )

                result = handler(weixin)
                return result

            return function
        return __wrapper__

    def text_filter(self, kw_filter):
        """
        为文本关键词注册一个处理器,
        需要注意, 此装饰器请勿与self.text同时使用, 因为此装饰器会注册
        一个处理text处理器来进行关键词的路由
        """

        if isinstance(kw_filter, list):

            # 关键词数组, 编译关键词表达式
            regex = '^\s*(%s)\s*$' % '|'.join(kw_filter)
            kw_filter = re.compile(regex)

        elif isinstance(kw_filter, str):

            # 编译自定义的正则表达式
            kw_filter = re.compile(kw_filter)

        elif not isinstance(kw_filter, re._pattern_type):

            # 既不是关键词数组也不是字符串正则表达式, 也不是编译好的表达式
            raise Exception(
                "kw_filter type is not list, str or re_pattern.")

        def __wrapper__(function):
            """
            注册关键词处理函数, 因为需要截获文本消息来匹配关键词, 所以这里会
            自动生成一个处理text类型消息的处理器, 所以当使用关键词时, 你不可以再使用
            Weechat.text 类型装饰器。
            """

            self.text_filter_handlers.append((kw_filter, function))

            @self.text
            def handle_text_message(weixin):
                ##
                # 注册自定义的text类型消息处理器, 此处理器用于关键词路由
                ##
                content = weixin.message.Content
                for cpre, h in self.text_filter_handlers:
                    if cpre.match(content):
                        handler = h
                        break
                else:
                    # 无匹配关键词, 调用默认处理器
                    handler = self.text_filter_default

                result = handler(weixin)
                return result

            return function
        return __wrapper__

    def on_finish(self, function):
        """
        每次请求结束后调用（注意只是消息渲染完成, 并不是消息已发送）, 不可做耗时工作
        被装饰方法同样可以获取到request, 返回值会被忽略
        """
        self.add_base_handler("_on_finish_", function)
        return function

    def _get_msg_type_key(self, message):
        """
        依据消息中的MsgType信息合成获取对应handler的key
        """
        key = self.uniform(message.MsgType)
        if key and key == self.uniform("EVENT"):
            key = "EVENT_%s" % message.Event

        return key

    def reply(self, xmlbody):
        """
        解析xml并查找对应处理器对消息做出回应,返回以渲染的xml字符串
        """
        req = WeixinRequest(self.config, xmlbody)

        key = self._get_msg_type_key(req.message)
        # 检查key是否存在, 不存在可能是因为
        # 发送的是加密消息, 而enc_aeskey未设置导致获取属性时返回None
        if not key:
            return

        # 获取处理器
        processer = self.get_base_handler(key)
        on_finish = self.get_base_handler("_on_finish_")
        result = processer(req)
        on_finish(req)

        xml = req.get_response_xml(default=result)
        return xml

__all__ = ['Weechat',]
