# encoding=utf-8
from .utils import AttributeDict, json_loads

__all__ = ['Config',]


class Config(AttributeDict):
    """
    配置类, 存储一些应用配置
    基于字典类型, 扩展支持使用属性的方式访问（单层）
    初始化时支持传入字典或者任意关键词。
    """
    def from_object(self, config_object, lower_keys=False):
        """
        从配置类读取配置, 会读取除__name__格式的所有属性。
        """
        for k in dir(config_object):
            if not k.startswith('__') and not k.endswith('__'):
                if lower_keys:
                    k = k.lower()
                self[k] = getattr(config_object, k)

    def from_dict(self, config_dict):
        """
        从字典读取配置
        """
        d = config_dict
        list(map(lambda k: self.set(k, d[k]), d))
        return

    def from_json(self, config_json):
        """
        从JSON字符串中读取配置
        """
        config = json_loads(config_json)
        self.from_dict(config)
