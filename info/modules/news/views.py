from flask import render_template, session, current_app, g, abort, jsonify, request

from info import constants, db
from info.models import User, News
from info.modules.news import news_blu
from info.utils.common import user_login
from info.utils.response_code import RET


@news_blu.route("/news_collect", methods=["POST"])
@user_login
def news_collect():
    """
    1.接收参数
    2.校验参数
    3.收藏新闻和取消收藏
    4.返回响应
    :return:
    """
    user = g.user

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ['collect','cancel_collect']:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="数据格式不正确")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="该条新闻不存在")

    # 下面执行业务逻辑
    if action == "collect":
        # 当收藏一条新闻的时候，应该先去判断是否已收藏
        if news in user. collection_news:
            user.collection_news.append(news)
        else:
            if news in user.collection_news:
                user.collection_news.remove(news)

        return jsonify(errno=RET.OK, errmsg="OK")





@news_blu.route("/<int:news_id>")
@user_login
def detail(news_id):
    """
    详情页面渲染
    :param news_id:
    :return:
    """
    user = g.user
    clicks_news = []
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)


    clicks_news_li = [news.to_basic_dict() for news in clicks_news]

    # 显示新闻的具体信息
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    if not news:
        abort(404)

    news.clicks += 1

    # 详情页收藏和已收藏是有is_collected控制
    is_collected = False
    # 1.保证用户存在
    # 2.新闻肯定存在
    # 3.该条新闻在用户收藏的列表中
    # 4.用户收藏新闻的列表——>user.collection_news.all()
    if user and news in user.collection_news.all():
        is_collected = True

    data = {
        "user_info":user.to_dict() if user else None,
        "clicks_news_li":clicks_news_li,
        "news":news.to_dict(),
        "is_collected":is_collected
    }


    return render_template("news/detail.html", data=data)

