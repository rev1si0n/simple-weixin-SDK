# encoding=utf-8
from .utils import AttributeDict, json_loads

__all__ = ['Config',]


class Config(AttributeDict):

    def from_object(self, config_object, lower_keys=False):
        for k in dir(config_object):
            if not k.startswith('__') and not k.endswith('__'):
                if lower_keys:
                    tk = k.lower()
                else:
                    tk = k
                self[tk] = getattr(config_object, k)

    def from_dict(self, config_dict):
        d = config_dict
        list(map(lambda k: self.set(k, d[k]), d))
        return

    def from_json(self, config_json):
        config = json_loads(config_json)
        self.from_dict(config)
