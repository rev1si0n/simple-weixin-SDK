# encoding=utf-8
from .utils import AttributeDict

class Config(AttributeDict):
    """
    配置类, 存储一些应用配置
    基于字典类型, 扩展支持使用属性的方式访问
    """
    pass
