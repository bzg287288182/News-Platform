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


    # if not news_id:
    #     abort(404)
    # try:
    #     news_id = int(news_id)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     abort(404)

    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        abort(404)

    news.clicks += 1


    data = {
        "user_info":user.to_dict() if user else None,
        "clicks_news_li":clicks_news_li,
        "news":news.to_dict()
    }


    return render_template("news/detail.html", data=data)

