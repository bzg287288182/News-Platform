from flask import render_template, redirect, current_app, send_file, session, request, jsonify
from info import redis_store, constants
from info.models import User, News, Category
from info.modules.index import index_blu
from info.utils.response_code import RET


@index_blu.route("/news_list")
def get_news_list():
    """
    1.接收参数，cid page per_page
    2.校验参数合法性
    3.查询出新闻
    4.返回响应
    :return:
    """
    cid = request.args.get("cid")
    page = request.args.get("page", 1)
    per_page = request.args.get("per_page", 10)

    try:

        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3.查询出的新闻（关系分类）（创建时间的排序）
    filters = []
    if cid != 1:
        filters.append(News.category_id == cid)

    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)

        # if cid == 1:
        #     paginate = News.query.filter().order_by(News.create_time.desc()).paginate(page, per_page, False)
        # else:
        #     paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(page, per_page, False)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    news_list = paginate.items
    current_page = paginate.page
    total_page = paginate.pages

    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    data = {
        "news_dict_li":news_dict_li,
        "current_page":current_page,
        "total_page":total_page
    }

    return jsonify(errno=RET.OK, errmsg="ok", data=data)


@index_blu.route("/")
def index():
    # redis_store.set("name","laowang")
    # 当进入首页，判断是否登录，如果登录，查处信息，渲染
    # 1.自身是一个容器
    # 2.sid 加密 cookie给了浏览器 sid == None 状态已经失效
    # 3.sid 加密 以sid为key {"user_id":"2"} value不存在redis
    user_id = session.get("user_id")

    user = None
    if user_id:
        try:
            user = User.query.get(user_id)  # user是一个obj
        except Exception as e:
            current_app.logger.error(e)

    # 1. 显示新闻列表显示
    clicks_news = []
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()  # [obj,obj,obj...]
    except Exception as e:
        current_app.logger.error(e)


    # clicks_news_li = []
    clicks_news_li = [news_obj.to_basic_dict() for news_obj in clicks_news ]
    # for news_obj in clicks_news:
    #     clicks_news_dict = news_obj.to_basic_dict()
    #     clicks_news_li.append(clicks_news_dict)

    # [{},{},{}]
    # 2.显示新闻分类
    categorys = []
    try:
        categorys = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)

    # category_li = []
    # for category in categorys:
    #     categorys_dict = category.to_dict()
    #     category_li.append(categorys_dict)

    category_li = [category.to_dict() for category in categorys]

    # data = {
    #     "user_info":user
    #     "nick_name":"laozhang",
    #     "mobile":"123456"
    #
    # }

    # 如果uer为空，那么传一个None， 如果不为空，user.to_dict()
    data = {
        "user_info":user.to_dict() if user else None,
        "clicks_news_li":clicks_news_li,
        "categorys":category_li
    }


    return render_template("news/index.html", data=data)


@index_blu.route("/favicon.ico")
def favicon():
    # 返回图片
    # return redirect("/static/news/favicon.ico")
    return current_app.send_static_file("news/favicon.ico")
    # return send_file("/static/news/favicon.ico")