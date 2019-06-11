from flask import render_template, session, current_app, g, abort

from info import constants, db
from info.models import User, News
from info.modules.news import news_blu
from info.utils.common import user_login


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

