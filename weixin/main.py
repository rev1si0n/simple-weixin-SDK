# encoding=utf-8
import re

from .config import Config
from .crypto import XMLMsgCryptor
from .request import WeixinRequest
from .storage import Sqlite3Storage


class Weechat(object):

    def __init__(self, token=None, appid=None, appsec=None, enc_aeskey=None):
        """
        最主要的类, 保存应用的各种配置信息以及路由信息, 且负责各种类型消息的路由
        """
        self.config = Config()

        # 存储token, appid, appsec
        self.add_config("token", token)
        self.add_config("appid", appid)
        self.add_config("appsec", appsec)
        self.add_config("enc_aeskey", enc_aeskey)

        default = lambda req: None

        self.handlers = dict()

        # 未知消息类型的处理器
        self.default = default

        # 关键字处理器数组
        self.text_filter_handlers = []
        # 默认关键字无匹配处理器
        self.text_filter_default = default

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
        >>> app.add_config('sqlconn', DB_CONNECTION)
        >>> ...
        >>>
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

    def uniform(self, key):
        """
        将key转换为大写
        """
        return key.upper()

    def add_base_handler(self, key, function):
        """
        设置一个对应MsgType的处理器
        """
        key = self.uniform(key)
        self.handlers[key] = function
        return

    def get_base_handler(self, key_list):
        """
        根据消息key列表找出对应的处理器，如果没找到则返回的是默认处理器
        """
        for k in key_list:
            k = self.uniform(k)
            h = self.handlers.get(k, None)
            if callable(h):
                return h

        return self.default

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
        """
        self.add_base_handler("event_subscribe", function)
        return function

    def unsubscribe_event(self, function):
        """
        装饰 MsgType=event, Event=unsubscribe 的处理器
        """
        self.add_base_handler("event_unsubscribe", function)
        return function

    def location_event(self, function):
        """
        装饰 MsgType=event, Event=location 的处理器
        """
        self.add_base_handler("event_location", function)
        return function

    def view_event(self, function):
        """
        装饰 MsgType=event, Event=view 的处理器
        """
        self.add_base_handler("event_view", function)
        return function

    def click_event(self, function):
        """
        装饰 MsgType=event, Event=click 的处理器
        """
        self.add_base_handler("event_click", function)
        return function

    def click_event_filter(self, key):
        """
        为click事件的一个eventkey绑定一个处理器
        """
        def register(function):
            # 注册点击事件的处理器
            k = "event_click_%s" % key
            self.add_base_handler(k, function)
            return function

        return register

    def scan_event_filter(self, scene):
        """
        为scan事件的一个场景绑定一个处理器
        """
        def register(function):
            # 注册点击事件的处理器
            k = "event_scan_%s" % scene
            self.add_base_handler(k, function)
            return function

        return register

    def subscribe_event_filter(self, scene):
        """
        为subscribe事件的一个场景绑定一个处理器
        """
        def register(function):
            # 注册点击事件的处理器
            k = "event_subscribe_%s" % scene
            self.add_base_handler(k, function)
            return function

        return register

    def _compile_text_filter(self, filter_):
        if isinstance(filter_, list):
            # 关键词数组, 编译关键词表达式
            regex = '^\s*(%s)\s*$' % '|'.join(filter_)
            return re.compile(regex)

        elif isinstance(filter_, str):
            # 编译自定义的正则表达式
            return re.compile(filter_)

        elif isinstance(filter_, re._pattern_type):
            # 已编译的正则表达式，直接返回
            return filter_

        raise Exception(
            "filter is not list, str or re_pattern.")

    def text_filter(self, kw_filter):
        """
        为文本关键词注册一个处理器,
        需要注意, 此装饰器请勿与self.text同时使用, 因为此装饰器会注册
        一个处理text处理器来进行关键词的路由
        """
        filter_ = self._compile_text_filter(kw_filter)

        def register(function):
            """
            注册关键词处理函数, 因为需要截获文本消息来匹配关键词, 所以这里会
            自动生成一个处理text类型消息的处理器, 所以当使用关键词时, 你不可以再使用
            Weechat.text 类型装饰器。
            """
            self.text_filter_handlers.append((filter_, function))

            @self.text
            def handle_text_message(request):
                ##
                # 注册自定义的text类型消息处理器, 此处理器用于关键词路由
                ##
                content = request.message.Content
                for cpre, h in self.text_filter_handlers:
                    if cpre.match(content):
                        break
                else:
                    # 无匹配关键词, 调用默认处理器
                    h = self.text_filter_default

                return h(request)
            # register return
            return function
        # decorator return
        return register

    def as_text_filter_default(self, function):
        """
        设置默认的关键词处理器（无匹配关键词时）
        """
        self.text_filter_default = function
        return function

    def on_finish(self, function):
        """
        每次请求结束后调用（注意只是消息渲染完成, 并不是消息已发送）, 不可做耗时工作
        被装饰方法同样可以获取到request, 返回值会被忽略
        """
        self.add_base_handler("_on_finish_", function)
        return function

    def _get_msg_handler_key(self, message):
        """
        依据消息中的MsgType信息合成获取对应handler的key
        """
        mtype = self.uniform(message.MsgType)
        if mtype and mtype == self.uniform("EVENT"):
            ev = self.uniform(message.Event)

            main_h_key = "EVENT_%s" % ev
            # 这几个事件都是有一个固定key的, 所以直接拼接成
            # 给主路由获取处理器用的key

            if ev in ("CLICK", "SCAN", "SUBSCRIBE",):
                ev_key = self.uniform(message.EventKey)
                sub_h_key = "EVENT_%s_%s" % (ev, ev_key)

                return sub_h_key, main_h_key
            else:
                return main_h_key,

        return mtype,

    def reply(self, xmlbody):
        """
        解析xml并查找对应处理器对消息做出回应,返回以渲染的xml字符串
        """
        req = WeixinRequest(self.config, xmlbody)

        key = self._get_msg_handler_key(req.message)
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
