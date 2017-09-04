# encoding=utf-8
import functools
import tornado.web
from ..utils import is_valid_request

def weixin_request_only(func):
    '''
    使用此装饰器装饰请求处理函数 get/post/...。
    那么仅有发来 signature, timestamp, nonce参数并且
    通过校验，请求才会被转交到处理函数, 否则一律返回状态码 401
    '''
    @functools.wraps(func)
    def _wrapper_(req):
        nts = map(lambda k: req.get_query_argument(k, ""),
                  ['nonce', 'timestamp', 'signature'])
        nonce, timestamp, sig = nts
        token = req.config.token

        if is_valid_request(token, nonce, timestamp, sig):
            return func(req)

        req.set_status(403)

    return _wrapper_


def make_handler(weapp):
    """
    生成一个tornado RequestHandler
    """

    class WeixinRequestHandler(tornado.web.RequestHandler):

        def initialize(self):
            """
            绑定一下weapp, 请求验证需要使用
            """
            self.weapp = weapp
            self.config = weapp.config

        def compute_etag(self):
            """
            响应无需缓存, 不计算etag
            """
            return

        def set_default_headers(self):
            """
            清除无用响应头
            """
            self.clear_header('Server')

        @weixin_request_only
        def get(self):
            """
            响应微信服务器验证请求
            """
            echo_str = self.get_argument ('echostr', "")
            self.finish(echo_str)

        @weixin_request_only
        async def post(self):
            """
            响应微信POST请求, async并没卵用
            """
            xml = self.weapp.reply(self.request.body) or ""
            self.write(xml)

    return WeixinRequestHandler
