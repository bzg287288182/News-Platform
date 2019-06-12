from flask import render_template, session, current_app, g, abort, jsonify, request

from info import constants, db
from info.models import User, News, Comment, CommentLike
from info.modules.news import news_blu
from info.utils.common import user_login
from info.utils.response_code import RET


@news_blu.route("/comment_like", methods=["POST"])
@user_login
def comment_like():
    """
    1.接收参数
    2.校验参数
    3.CommentLike()往点赞的表中添加或删除一条数据
    4.返回响应
    :return:
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg="用户未登录")

    comment_id = request.json.get("comment_id")
    action = request.json.get("action")

    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    if action not in ["add", "remove"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        comment_id = int(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        comment_obj = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA, errmsg="数据库查询错误")

    if not comment_id:
        return jsonify(errno=RET.NODATA,errmsg="该评论不存在")

    comment_like_obj = CommentLike.query.filter_by(comment_id=comment_id, user_id=user.id).first()
    # 业务逻辑
    if action == "add":
        # 如果添加一条评论，要初始化一个评论对象，并将数据添加进去，
        if not comment_like_obj:
            comment_like = CommentLike()
            comment_like.comment_id = comment_id
            comment_like.user_id = user.id
            db.session.add(comment_like)
            comment_obj.like_count += 1
            db.session.commit()

    else:
        # 如果这条点赞存在，才能删除
        if comment_like_obj:
            db.session.delete(comment_like_obj)
            comment_obj.like_count -= 1
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(errno=RET.DBERR,errmsg="数据库保存失败")

    return jsonify(errno=RET.OK, errmsg="OK")



@news_blu.route("/news_comment", methods=["POST"])
@user_login
def news_comment():
    """
    1.接收参数，用户 新闻 评论内容 parant_id
    2.校验参数
    3.业务逻辑
    4.返回响应
    :return:
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 1. 取到请求参数
    news_id = request.json.get("news_id")
    comment_str = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    # 2. 判断参数
    if not all([news_id, comment_str]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 查询新闻，并判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到新闻数据")

    # 3. 初始化一个评论模型，并且赋值
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_str
    if parent_id:
        comment.parent_id = parent_id

    # 添加到数据库
    # 为什么要自己去commit()?，因为在return的时候需要用到 comment 的 id
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")
    return jsonify(errno=RET.OK, errmsg="OK", data=comment.to_dict())



@news_blu.route("/news_collect", methods=["POST"])
@user_login
def news_collect():
    print(22222222222)
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

    comments = []
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    comment_dict_li = []

    for comment in comments:
        comment_dict = comment.to_dict()
        comment_dict["is_like"] = False
        # 如果comment_dict["is_like"] = True 代表已经点赞
        # 如果该条评论的id在我的点赞id列表中
        if user and CommentLike.query.filter(CommentLike.comment_id==comment.id, CommentLike.user_id==user.id).first():
            comment_dict["is_like"] = True

        comment_dict_li.append(comment_dict)


    data = {
        "user_info":user.to_dict() if user else None,
        "clicks_news_li":clicks_news_li,
        "news":news.to_dict(),
        "is_collected":is_collected,
        "comments": comment_dict_li
    }


    return render_template("news/detail.html", data=data)

