from flask import render_template, redirect, current_app, send_file, session
from info import redis_store
from info.models import User
from info.modules.index import index_blu


@index_blu.route("/")
def index():
    # redis_store.set("name","laowang")
    # 当进入首页，判断是否登录，如果登录，查处信息，渲染
    user_id = session.get("user_id")

    user = None
    if user_id:
        try:
            user = User.query.get(user_id)  # user是一个obj
        except Exception as e:
            current_app.logger.error(e)

    # data = {
    #     "user_info":user
    #     "nick_name":"laozhang",
    #     "mobile":"123456"
    #
    # }

    # 如果uer为空，那么传一个None， 如果不为空，user.to_dict()
    data = {
        "user_info":user.to_dict() if user else None
    }


    return render_template("news/index.html", data=data)






@index_blu.route("/favicon.ico")
def favicon():
    # 返回图片
    # return redirect("/static/news/favicon.ico")
    return current_app.send_static_file("news/favicon.ico")
    # return send_file("/static/news/favicon.ico")