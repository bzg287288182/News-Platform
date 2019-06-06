import logging
from redis import StrictRedis


# __all__ = ["DevelopConfig", "Config","ProductConfig","TestingConfig"]


class Config(object):
    SECRET_KEY = "12421312"
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/Information"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 给配置类里面自定义了两个类属性
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379


    # 制定session的储存方式
    SESSION_TYPE = "redis"
    #制定储存session的储存对象
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    # 设置session签名 加密
    SESSION_USE_SIGNER = True
    # 设置session 永久保存
    SESSION_PERMANENT = False
    # 设置session保存时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2




class DevelopConfig(Config):
    DEBUG = True
    LOG_LEVEL = logging.ERROR


class ProductConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    DEBUG = True



# 使用字典去封装
config = {
    "develop":DevelopConfig,
    "product":ProductConfig,
    "testing":TestingConfig
}