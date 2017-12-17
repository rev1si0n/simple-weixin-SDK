# encoding=utf-8

class BaseSession(object):

    def session_id(self):
        raise NotImplementedError

    def save(self, expires=86400):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __getitem__(self, key):
        raise NotImplementedError


class Session(BaseSession):

    def __init__(self, req):
        self.dict = {}
        self.storage = req.config.storage
        self.openid = req.message.FromUserName
        # 从数据库读取并加载会话信息
        session = self.storage.get(
            self.session_id(),
            encoding="utf-8"
        ) or {}
        self.dict.update(session)

    def session_id(self):
        # self._openid 必须要在先前被设置
        return "session:%s" % self.openid

    def save(self, expires=7*86400):
        self.storage.set(
            self.session_id(),
            self.dict,
            expires
        )

    def destroy(self):
        self.dict = {}
        self.storage.delete(self.session_id())

    def __call__(self, key, value=None):
        if value is not None:
            self.__setitem__(key, value)

        return self.__getitem__(key)

    def __setitem__(self, key, value):
        self.dict[key] = value

    def __getitem__ (self, key):
        try:
            return self.dict[key]

        except KeyError:
            return
