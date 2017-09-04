## ！项目目前处于开发阶段

项目当前大部分功能通过了测试，但是微信api（server_api）部分未完全经过测试，且此模块未完整实现所有接口

### 操蛋的使用方法
暂且是开发版本，只给出简单示例。

> 通用应用设置
``` python
# application config.py

from weixin.main import Weechat
from weixin.server_api import Client
from weixin.storage import Sqlite3Storage


app = Weechat()

# 会话信息，ACCESS TOKEN存储器，也是一个简单的key->value存储器
# 目前已实现 Mysql, Redis, Sqlite3 数据库，多实例部署的情况下不建议使用 Sqlite3 存储器
app.set_storage(Sqlite3Storage())

# 微信基础配置
app.add_config("token", WEIXIN_TOKEN)
app.add_config("appid", WEIXIN_APPID)
app.add_config("appsec", WEIXIN_APPSEC)

# enc_aeskey 必须在前三项设置完毕后才可设置，如果不为None则会使用该密钥对消息加解密
app.set_enc_aeskey(WEIXIN_ENCAESKEY)

# api client
app.add_config("client", Client(app.config))

# 其他配置
dino.add_config("database", MYSQL_CONNECTION)
dino.add_config("app_base_url", "http://example.com")
```
> 应用实现

``` python
# application handlers.py

from weixin.reply import Text
from weixin.utils import make_link

from .config import app


@app.click_event_filter('settings') # 此方法可以处理处理菜单点击的key
@app.text_filter(['设置', '設置']) # 此方法可以处理文本消息关键词
def settings(request):
    """
    回复设置链接
    """
    base_url = request.config.app_base_url
    content = "🔧" + make_link("点击进入设置", base_url + "/settings")
    request.response(Text, content)
    return

# ....

```

> web框架配置（此处为tornado）
``` python
# application web.py

import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.options import define, options

from weixin.framwork.tornado import make_handler

from .config import app
from .handlers import* # 导入handlers

define("port", default=2345, help="port", type=int)


if __name__ == "__main__":
    options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(
        tornado.web.Application(
            handlers=[("/myapp", make_handler(app)), ],
            debug=True
        ),
        xheaders=True
    )

    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
```

> 定时刷新access_token
怎么实现就不关我的事了，你可以crontab，或者celery定时任务每小时刷新一遍
``` python
# application refresh_token.py

from .config import app

def refresher():
    app.config.client.refresh_access_token()

if __name__ == "__main__":
    refresher()
```

上面的示例代码直接copy去肯定无法运行，这个代码只是作为简单示例。

## License

[MIT](LICENSE)
