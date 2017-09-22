## ！项目目前处于开发阶段

项目当前大部分功能通过了测试，但是微信api（server_api）部分未完全经过测试，且此模块未完整实现所有接口，只支持Python3.4+版本

### 安装
``` bash
pip3 install https://github.com/thisforeda/weixin-Python-SDK/archive/master.zip # 安装
pip3 install -U https：//... # 升级
```


### 框架流程简述

用户首先初始化一个 Weechat实例`weixin.main.Weechat`。此实例包含了应用的所有配置。实例包含一个重要的方法`reply`，此方法只接受一个参数，即微信POST过来的消息体，这也是唯一一个需要自己与所使用Web框架结合的方法，参见`weixin.framework.tornado`的实现方法。

当你的应用运行时，Web框架的相关代码获取微信POST的消息体，交由`Weechat.reply`，此时`Weechat`会解析此消息，判断消息类型和内容后，根据消息类型（event, ..)或内容（keyword, ..），在注册过的处理器中查找用户注册（装饰）的处理器。找到了则交给用户注册的函数进行处理，否则调用默认的处理器（你也可以注册某些默认处理器）。

处理器应只接受一个参数 `request`，此参数意义上类似于Django view中的request，或是tornado的RequestHandler。在此参数里你可以访问到应用的全局配置。当你的函数处理完毕后，如果有输出，请调用 `request.reply`来返回一些内容。


### 操蛋的使用方法
暂且是开发版本，只给出简单示例。

> 通用应用设置
``` python
# application config.py

from weixin.main import Weechat
from weixin.client_api import Client
from weixin.storage import Sqlite3Storage


app = Weechat()

# 会话信息，ACCESS TOKEN存储器，也是一个简单的key->value存储器
# 目前已实现 Mysql, Redis, Sqlite3 数据库，多实例部署的情况下不建议使用 Sqlite3 存储器
app.set_storage(Sqlite3Storage())

# 微信基础配置
app.add_config("token", WEIXIN_TOKEN)
app.add_config("appid", WEIXIN_APPID)
app.add_config("appsec", WEIXIN_APPSEC)
app.add_config("enc_aeskey", WEIXIN_ENCAESKEY)

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

from weixin.framework.tornado import make_handler

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
