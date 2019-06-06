"""
1.集成配置类
2.集成sqalchemy到flask
3.集成redis
4.集成csrfrotect
5.集成flask-session
6.集成flask-script
7.集成flask-migrate
"""
import logging
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from info import create_app,db

# 通过传入不同配置，创造出不同配置下的app实例,工厂方法　python设计模式:工厂模式
app = create_app("develop")



# 6.集成flask-script
manager = Manager(app)

# 7.集成flask-migrate， 在flask中对数据库进行迁移
Migrate(app,db)
manager.add_command("db", MigrateCommand)


@app.route('/')
def index():
    logging.debug("debug")
    logging.error("error")
    logging.warning(("warning"))
    logging.info("info")
    logging.fatal("fatal")

    return 'Hello World'

if __name__ == '__main__':
    app.run()