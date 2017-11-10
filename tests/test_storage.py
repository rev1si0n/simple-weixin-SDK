# encoding=utf-8
import time
import pytest
from weixin.storage import *


@pytest.mark.parametrize("storage", [
    Sqlite3Storage(),
    RedisStorage(),
    MySQLStorage("mysql://root:@127.0.0.1/test"),
])
def test_storage(storage):

    storage.set("key", "value")
    assert storage.get("key") == b"value"
    assert storage.get("key", encoding="utf-8") == "value"
    
    storage.delete("key")
    assert storage.get("key") == None
    assert storage.get("key_not_exist") == None

    storage.set("key", "value", expires=1)
    time.sleep(3)
    assert storage.get("key") == None
    assert storage.is_expired("key")
    assert storage.is_expired("key_not_exist")

    for index in range(36):
        storage.set("prefix_%s" % index, "value")

    lists = storage.get_all_keys_by_wildcard(wildcard='prefix_*')
    assert len(lists) == 36
    
    assert isinstance(storage.get_ttl("key_not_exist"), int)

