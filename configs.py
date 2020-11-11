import configparser
import os

env = os.environ

cf = configparser.ConfigParser()
thisdir = os.path.dirname(__file__)
cf.read(os.path.join(thisdir, '.conf'))

# datacenter
DC_HOST = env.get("DC_HOST", cf.get('dc', 'DC_HOST'))
DC_PORT = int(env.get("DC_PORT", cf.get('dc', 'DC_PORT')))
DC_USER = env.get("DC_USER", cf.get('dc', 'DC_USER'))
DC_PASSWD = env.get("DC_PASSWD", cf.get('dc', 'DC_PASSWD'))
DC_DB = env.get("DC_DB", cf.get('dc', 'DC_DB'))

# deploy
LOCAL = bool(int(env.get("LOCAL", cf.get('deploy', 'LOCAL'))))
VPN = bool(int(env.get("LOCAL", cf.get('deploy', 'VPN'))))
FIRST = bool(int(env.get("FIRST", cf.get('deploy', 'FIRST'))))
SECRET = env.get("SECRET", cf.get('deploy', 'SECRET'))
TOKEN = env.get("TOKEN", cf.get('deploy', 'TOKEN'))
PROXY_URL = env.get("PROXY_URL", cf.get("deploy", "PROXY_URL"))
LOCAL_PROXY_URL = env.get("LOCAL_PROXY_URL", cf.get("deploy", "LOCAL_PROXY_URL"))


# test
TEST_MYSQL_HOST = env.get("TEST_MYSQL_HOST", cf.get('test', 'TEST_MYSQL_HOST'))
TEST_MYSQL_PORT = int(env.get("TEST_MYSQL_PORT", cf.get('test', 'TEST_MYSQL_PORT')))
TEST_MYSQL_USER = env.get("TEST_MYSQL_USER", cf.get('test', 'TEST_MYSQL_USER'))
TEST_MYSQL_PASSWORD = env.get("TEST_MYSQL_PASSWORD", cf.get('test', 'TEST_MYSQL_PASSWORD'))
TEST_MYSQL_DB = env.get("TEST_MYSQL_DB", cf.get('test', 'TEST_MYSQL_DB'))

# 聚源
if not VPN:
    JUY_HOST = env.get("JUY_HOST", cf.get('juyuan', 'JUY_HOST'))
    JUY_PORT = int(env.get("JUY_PORT", cf.get('juyuan', 'JUY_PORT')))
    JUY_USER = env.get("JUY_USER", cf.get('juyuan', 'JUY_USER'))
    JUY_PASSWD = env.get("JUY_PASSWD", cf.get('juyuan', 'JUY_PASSWD'))
    JUY_DB = env.get("JUY_DB", cf.get('juyuan', 'JUY_DB'))
else:
    JUY_HOST = env.get("JUY_HOST", cf.get('vjuyuan', 'JUY_HOST'))
    JUY_PORT = int(env.get("JUY_PORT", cf.get('vjuyuan', 'JUY_PORT')))
    JUY_USER = env.get("JUY_USER", cf.get('vjuyuan', 'JUY_USER'))
    JUY_PASSWD = env.get("JUY_PASSWD", cf.get('vjuyuan', 'JUY_PASSWD'))
    JUY_DB = env.get("JUY_DB", cf.get('vjuyuan', 'JUY_DB'))


# spider 读写
if LOCAL:
    SPIDER_MYSQL_HOST = TEST_MYSQL_HOST
    SPIDER_MYSQL_PORT = TEST_MYSQL_PORT
    SPIDER_MYSQL_USER = TEST_MYSQL_USER
    SPIDER_MYSQL_PASSWORD = TEST_MYSQL_PASSWORD
    SPIDER_MYSQL_DB = TEST_MYSQL_DB
else:
    SPIDER_MYSQL_HOST = env.get("SPIDER_MYSQL_HOST", cf.get('spider', 'SPIDER_MYSQL_HOST'))
    SPIDER_MYSQL_PORT = int(env.get("SPIDER_MYSQL_PORT", cf.get('spider', 'SPIDER_MYSQL_PORT')))
    SPIDER_MYSQL_USER = env.get("SPIDER_MYSQL_USER", cf.get('spider', 'SPIDER_MYSQL_USER'))
    SPIDER_MYSQL_PASSWORD = env.get("SPIDER_MYSQL_PASSWORD", cf.get('spider', 'SPIDER_MYSQL_PASSWORD'))
    SPIDER_MYSQL_DB = env.get("SPIDER_MYSQL_DB", cf.get('spider', 'SPIDER_MYSQL_DB'))

# spider2 只读
if not VPN:
    SPIDER_MYSQL_HOST2 = env.get("SPIDER_MYSQL_HOST2", cf.get('spider2', 'SPIDER_MYSQL_HOST2'))
    SPIDER_MYSQL_PORT2 = int(env.get("SPIDER_MYSQL_PORT2", cf.get('spider2', 'SPIDER_MYSQL_PORT2')))
    SPIDER_MYSQL_USER2 = env.get("SPIDER_MYSQL_USER2", cf.get('spider2', 'SPIDER_MYSQL_USER2'))
    SPIDER_MYSQL_PASSWORD2 = env.get("SPIDER_MYSQL_PASSWORD2", cf.get('spider2', 'SPIDER_MYSQL_PASSWORD2'))
    SPIDER_MYSQL_DB2 = env.get("SPIDER_MYSQL_DB2", cf.get('spider2', 'SPIDER_MYSQL_DB2'))
else:
    SPIDER_MYSQL_HOST2 = env.get("SPIDER_MYSQL_HOST2", cf.get('vspider2', 'SPIDER_MYSQL_HOST2'))
    SPIDER_MYSQL_PORT2 = int(env.get("SPIDER_MYSQL_PORT2", cf.get('vspider2', 'SPIDER_MYSQL_PORT2')))
    SPIDER_MYSQL_USER2 = env.get("SPIDER_MYSQL_USER2", cf.get('vspider2', 'SPIDER_MYSQL_USER2'))
    SPIDER_MYSQL_PASSWORD2 = env.get("SPIDER_MYSQL_PASSWORD2", cf.get('vspider2', 'SPIDER_MYSQL_PASSWORD2'))
    SPIDER_MYSQL_DB2 = env.get("SPIDER_MYSQL_DB2", cf.get('vspider2', 'SPIDER_MYSQL_DB2'))


# 内网舆情测试库
if LOCAL:
    YQ_HOST = env.get("YQ_HOST", cf.get('yuqing', 'YQ_HOST'))
    YQ_PORT = env.get("YQ_PORT", cf.get('yuqing', 'YQ_PORT'))
    YQ_USER = env.get("YQ_USER", cf.get('yuqing', 'YQ_USER'))
    YQ_PASSWD = env.get("YQ_PASSWD", cf.get('yuqing', 'YQ_PASSWD'))
    YQ_DB = env.get("YQ_DB", cf.get('yuqing', 'YQ_DB'))
else:
    YQ_HOST = env.get("YQ_HOST", cf.get('yuqing2', 'YQ_HOST'))
    YQ_PORT = env.get("YQ_PORT", cf.get('yuqing2', 'YQ_PORT'))
    YQ_USER = env.get("YQ_USER", cf.get('yuqing2', 'YQ_USER'))
    YQ_PASSWD = env.get("YQ_PASSWD", cf.get('yuqing2', 'YQ_PASSWD'))
    YQ_DB = env.get("YQ_DB", cf.get('yuqing2', 'YQ_DB'))

# 通联库
TL_HOST = env.get("TL_HOST", cf.get('tonglian', 'TL_HOST'))
TL_PORT = env.get("TL_PORT", cf.get('tonglian', 'TL_PORT'))
TL_USER = env.get("TL_USER", cf.get('tonglian', 'TL_USER'))
TL_PASSWD = env.get("TL_PASSWD", cf.get('tonglian', 'TL_PASSWD'))
TL_DB = env.get("TL_DB", cf.get('tonglian', 'TL_DB'))

# 主题猎手数据库
THE_HOST = env.get("THE_HOST", cf.get('theme', 'THE_HOST'))
THE_PORT = env.get("THE_PORT", cf.get('theme', 'THE_PORT'))
THE_USER = env.get("THE_USER", cf.get('theme', 'THE_USER'))
THE_PASSWD = env.get("THE_PASSWD", cf.get('theme', 'THE_PASSWD'))
THE_DB = env.get("THE_DB", cf.get('theme', 'THE_DB'))

# product
if LOCAL:
    PRODUCT_MYSQL_HOST = TEST_MYSQL_HOST
    PRODUCT_MYSQL_PORT = TEST_MYSQL_PORT
    PRODUCT_MYSQL_USER = TEST_MYSQL_USER
    PRODUCT_MYSQL_PASSWORD = TEST_MYSQL_PASSWORD
    PRODUCT_MYSQL_DB = TEST_MYSQL_DB
else:
    PRODUCT_MYSQL_HOST = env.get("PRODUCT_MYSQL_HOST", cf.get('product', 'PRODUCT_MYSQL_HOST'))
    PRODUCT_MYSQL_PORT = env.get("PRODUCT_MYSQL_PORT", cf.get('product', 'PRODUCT_MYSQL_PORT'))
    PRODUCT_MYSQL_USER = env.get("PRODUCT_MYSQL_USER", cf.get('product', 'PRODUCT_MYSQL_USER'))
    PRODUCT_MYSQL_PASSWORD = env.get("PRODUCT_MYSQL_PASSWORD", cf.get('product', 'PRODUCT_MYSQL_PASSWORD'))
    PRODUCT_MYSQL_DB = env.get("PRODUCT_MYSQL_DB", cf.get('product', 'PRODUCT_MYSQL_DB'))


if __name__ == "__main__":
    import sys
    mod = sys.modules[__name__]
    attrs = dir(mod)
    attrs = [attr for attr in attrs if not attr.startswith("__") and attr.isupper()]
    for attr in attrs:
        print(attr, ":", getattr(mod, attr))
