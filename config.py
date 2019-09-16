import os
import redis


# 配置文件
class Config(object):
    # 关系型数据库的配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/apps'
    SECRET_KEY = os.urandom(24)

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # 非关系型数据库的配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    # 配置session的扩展,session类型
    SESSION_TYPE = 'redis'
    # 创建redis链接,有密码设置密码
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 是否对发送到浏览器上session的cookie值进行加密
    SESSION_USE_SIGNER = False
    PERMANENT_SESSION_LIFETIME = 60*60*24*2  # 生命周期
    SESSION_PERMANENT = False  # 如果设置为True,则关闭浏览器session就失效
    # SESSION_KEY_PREFIX = 'session:'  # 保存到session中的值的前缀
    # 配置CELERY
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379/7'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/7'


class DevConfig(Config):
    # 开发环境配置
    DEBUG = True
    PORT = 6000


class OnlineConfig(Config):
    # 发布环境
    pass

config = {
    'dev': DevConfig,
    'online': OnlineConfig,
}
