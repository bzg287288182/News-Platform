# 创建一个存放业务逻辑的包

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session


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
