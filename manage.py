"""
1.集成配置类
2.集成sqalchemy到flask
3.集成redis
4.集成csrfrotect
5.集成flask-session
6.集成flask-script
7.集成flask-migrate
"""

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from info import app,db

# 6.集成flask-script
manager = Manager(app)

# 7.集成flask-migrate， 在flask中对数据库进行迁移
Migrate(app,db)
manager.add_command("db", MigrateCommand)


@app.route('/')
def index():
    return 'Hello World'

if __name__ == '__main__':
    app.run()