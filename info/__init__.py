# 创建一个存放业务逻辑的包
from logging.handlers import RotatingFileHandler
from flask import Flask
import logging

from flask_wtf.csrf import generate_csrf
from config import config, Config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
# from info.modules.index import index_blu

# config = {
#     "develop":DevelopConfig,
#     "product":ProductConfig,
#     "testing":TestingConfig
# }

db = SQLAlchemy()

redis_store = None  # type:index_blu


def set_log(config_name):
    # 通过不同的人的配置创建出不同的日志记录
    # 设置日志的记录等级
    logging.basicConfig(level=logging.DEBUG)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


# 只要是可变的参数，1,可以放在配置文件中，2.用函数封装 3.用全局变量
# 把所有可变的参数用函数的形参来代替
def create_app(config_name, ):
    global redis_store
    set_log(config_name)
    app = Flask(__name__)

    # 1.集成配置类

    app.config.from_object(config[config_name])
    # app.config.from_object(Config)
    # app.config.from_pyfile()
    # app.config.from_envvar()

    # 2.集成sqlalchemy到flask
    db.init_app(app)
    # db = SQLAlchemy(app)


    # 3.集成redis 可以把容易产生变化的值放入到配置中
    redis_store = StrictRedis(host=config["develop"].REDIS_HOST, port=config["develop"].REDIS_PORT, decode_responses=True)
    # redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

    # 4.CSRFProtect, 只起到保护的作用，具体往表单和Cookie中设置csrf_token还需要自己做
    # response = make_response("")
    # response.set_cookie("key", "value", max_age=秒数)


    # 1先网cookie中添加一个csrf_token
    # 2往表单中去设置，在ajax中设置一个csrf_token
    @ app.after_request
    def after_request(response):
        csrf_token = generate_csrf()
        response.set_cookie("csrf_token",csrf_token)

        return response
    CSRFProtect(app)

    # 集成flask-session
    # 说明：flask中的session是保存用户数据的容器（上下文）,而flask_session中的Session是制定session的保存路径
    Session(app)
    # 注册蓝图
    # 对于index_nlu只导入一次，什么时候调用，什么时候导入
    app.add_template_filter()


    from info.modules.index import index_blu
    app.register_blueprint(index_blu)

    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)

    return app
