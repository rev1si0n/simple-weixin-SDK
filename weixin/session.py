# encoding=utf-8

class BaseSession(object):
    '''
    会话基础类
    '''
    def session_id(self):
        '''
        获取会话唯一id, 基于HTTP时使用 uniqueid: get_cookie, get_secure_cookie
        基于微信时使用用户openid来判别
        '''
        raise NotImplementedError

    def save(self, expires=86400):
        '''
        存储会话
        '''
        raise NotImplementedError

    def destroy(self):
        '''
        销毁会话
        '''
        raise NotImplementedError

    def __setitem__(self, key, value):
        '''
        添加key,value
        '''
        raise NotImplementedError

    def __getitem__(self, key):
        '''
        获取key对应的值
        '''
        raise NotImplementedError


class Session(BaseSession):

    def __init__(self, req):
        ''' 初始化session信息, 从数据库读取并加载会话
        '''
        self.dict = {}
        # 从微信消息获取当前请求的 openid
        self.openid = req.message.FromUserName

        # 获取会话存取方法
        self.storage = req.config.storage

        # 从数据库读取并加载会话信息
        session = self.storage.get(self.session_id()) or {}
        self.dict.update(session)

    def session_id(self):
        # self._openid 必须要在先前被设置
        return "session:%s" % self.openid

    def save(self, expires=7*86400):
        '''
        保存会话，必须在每次改变会话信息后调用
        否则会话不会被存入数据库, expires 代表会话存活秒数
        '''
        self.storage.set(self.session_id(),
                         self.dict,
                         expires)

    def destroy(self):
        '''销毁会话, 这将会清空当前字典与数据库内容
        '''
        self.dict = {}
        self.storage.delete(self.session_id())

    def __call__(self, key, value=None):
        """
        >>> # 获取会话user的值
        >>> u = req.session("user")
        >>> # 设置会话user的值
        >>> req.session("user", "Zhang")
        """
        if value is not None:
            self.__setitem__(key, value)

        return self.__getitem__(key)

    def __setitem__(self, key, value):
        ''' session['hello'] = 'yes'
        '''
        self.dict[key] = value

    def __getitem__ (self, key):
        '''
        这里只是为了可以这样使用 : if self.session ['islogin']:...
        如果不存在 islogin 这个 key 的话会抛出异常, 这样的话,
        如果不存在这个 key 那么会返回 None
        '''
        try:
            return self.dict[key]

        except KeyError:
            return
