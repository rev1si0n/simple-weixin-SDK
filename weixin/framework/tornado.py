# encoding=utf-8
import functools
import tornado.web
from ..utils import is_valid_request

def weixin_request_only(func):
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

    weapp.initialize()
    class WeixinRequestHandler(tornado.web.RequestHandler):

        def initialize(self):
            self.weapp = weapp
            self.config = weapp.config

        def compute_etag(self):
            return

        def set_default_headers(self):
            self.clear_header('Server')

        @weixin_request_only
        def get(self):
            echo_str = self.get_argument ('echostr', "")
            self.finish(echo_str)

        @weixin_request_only
        async def post(self):
            xml = self.weapp.reply(self.request.body) or ""
            self.write(xml)

    return WeixinRequestHandler
