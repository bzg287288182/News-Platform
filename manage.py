

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class Config(object):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "mysql://root:"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

app = Flask(__name__)
# 集成配置类
app.config.from_object(Config)
app.config.from_pyfile()
app.config.from_envvar()

db = SQLAlchemy(app)


@app.route('/')
def index():
    return 'Hello World'

if __name__ == '__main__':
    app.run()