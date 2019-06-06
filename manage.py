

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect


class Config(object):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/Information"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 给配置类里面自定义了两个类属性
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379



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
CSRFProtect(app)

@app.route('/')
def index():
    redis_store.set("name","laobai")
    return 'Hello World'

if __name__ == '__main__':
    app.run()