# 创建一个存放业务逻辑的包

from flask import Flask
from config import config, Config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session



# config = {
#     "develop":DevelopConfig,
#     "product":ProductConfig,
#     "testing":TestingConfig
# }


db = SQLAlchemy()
# 只要是可变的参数，1,可以放在配置文件中，2.用函数封装 3.用全局变量
#把所有可变的参数用函数的形参来代替
def create_app(config_name,):
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
    redis_store = StrictRedis(host=config["develop"].REDIS_HOST,port=config["develop"].REDIS_PORT)
    # redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

    # 4.CSRFProtect, 只起到保护的作用，具体往表单和Cookie中设置csrf_token还需要自己做
    # response = make_response("")
    # response.set_cookie("key", "value", max_age=秒数)
    CSRFProtect(app)

    # 集成flask-session
    # 说明：flask中的session是保存用户数据的容器（上下文）,而flask_session中的Session是制定session的保存路径
    Session(app)

    return app
