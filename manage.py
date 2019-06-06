"""
1.集成配置类
2.集成sqalchemy到flask
5.集成flask-session
"""

from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session

class Config(object):
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


app = Flask(__name__)
# 1.集成配置类
app.config.from_object(Config)
# app.config.from_object(Config)
# app.config.from_pyfile()
# app.config.from_envvar()

# 2.集成sqlalchemy到flask
db = SQLAlchemy(app)

# 3.集成redis 可以把容易产生变化的值放入到配置中
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# 4.CSRFProtect, 只起到保护的作用，具体往表单和Cookie中设置csrf_token还需要自己做
# response = make_response("")
# response.set_cookie("key", "value", max_age=秒数)
CSRFProtect(app)

# 集成flask-session
# 说明：flask中的session是保存用户数据的容器（上下文）,而flask_session中的Session是制定session的保存路径
Session(app)




@app.route('/')
def index():
    redis_store.set("name","laobai")
    return 'Hello World'

if __name__ == '__main__':
    app.run()