from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
import redis
import logging
from logging.handlers import RotatingFileHandler


from config import config
# redis
redis_store = None
# 完成操作句柄的定义
db = SQLAlchemy()
# 全局保护
# csrf = CSRFProtect()

# 日志等级的设置
logging.basicConfig(level=logging.DEBUG)
# 创建日志记录器，每个日志路径，大小，保存日志的上限
# 这里参数是路径，最大存储内存，计数（因为默认是a模式，存满自动新增文件）
file_log_handler = RotatingFileHandler(
    filename='logs/log',
    maxBytes=1024 * 1024,
    backupCount=10)
# 设置日志格式　　　　　日志等级　　　　　日志信息　　　日志行数　
formatter = logging.Formatter('%(levelname)s %(message)s %(lineno)d')
# 将日志记录器指定日志格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象添加日志记录器
logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    # 根据运行的模式加载不同的配置对象
    app = Flask(__name__)
    # 配置文件是一个对下
    app.config.from_object(config[config_name])
    # 操作句柄关联app
    db.init_app(app)
    # 这都是关联app
    # csrf.init_app(app)
    Session(app)
    # cors
    CORS(app, supports_credentials=True, resources=r'/*')
    # redis
    global redis_store
    redis_store = redis.StrictRedis(
        host=config[config_name].REDIS_HOST,
        port=config[config_name].REDIS_PORT)
    # 注册蓝图,第二个参数是这个模块对应的开始路径,url_prefix前缀
    from apps.api_1_0 import api
    app.register_blueprint(api, url_prefix='/api/v1.0')

    return app


