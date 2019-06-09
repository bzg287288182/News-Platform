import random
import re
from flask import abort, request, current_app, make_response, jsonify, session

from info import constants, redis_store, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET


@passport_blu.route("/register")
def register():
    """
    1.接收参数 mobile， smscode， password
    2.整体校验参数的完整性
    3.手机号格式是否正确
    4.从redis中通过手机号取出真实的短信验证码
    5.和用户输入的验证吗进行校验
    6.初始化一个User（）添加数据
    7.session保持用户登录状态
    8.返回响应
    :return:
    """
    # 1.
    dict_data = request.json
    mobile = dict_data.get("mobile")
    smscode = dict_data("smscode")
    password = dict_data("password")

    # 2.
    if not all([mobile,smscode, password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # 3.
    if not re.match(r"1[35678]\d{6}", mobile):
        return jsonify(errno="", errmsg="验证码格式正确")

    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    if not real_sms_code:
        return jsonify(errno=RET.NODATA,errmsg="短信验证码已过期")

    if real_sms_code != smscode:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")


    user = User()
    user.nick_name = mobile
    user.password = password
    user.mobile = mobile

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库保存失败")

    # 7.
    session["user_id"] = user.id

    return jsonify(errno=RET.OK, errmsg="注册成功")


# 1.请求的url
# 2.请求的方式
# 3.请求的参数
# 4.返回给前段的参数和参数类型


@passport_blu.route("/sms_code", methods=["POST"])
def get_sms_code():
    """
    1.接收参数 mobile, image_code, image_code_id
    2.校验参数，mobile 正则
    3.校验用户输入的验证码和通过image_code_id查询出来的验证码是否一志
    4.先去定义一个随机的手机验证码
    5.调用云通讯发送手机验证码
    6.将验证码发送到redis
    7.给前段一个相应
    :return:
    """
    # 因为json类型实际是一个字符串类型，无法用到.get("mobile")
    # 需要将json转化称一个字典对象
    # json_data = request.data
    # dict_data = json.loads(json_data)
    # 如何去接收一个前段传入的json类型的数据


    dict_data = request.json

    # 1.接收参数 mobile, image_code, image_code_id
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")

    # 2.全局的做一个检验
    if not all([mobile,image_code,image_code_id]):
        return jsonify(errno="",errmsg="参数不全")

    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno="", errmsg="手机号格式正确")

    # 4.取出真实的验证码
    try:
        real_image_code = redis_store.get("ImageCodeId_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询失败")

    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码过期了")

    if image_code.upper() != real_image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码输入错误")

    # 核心逻辑
    #5.先定义一个
    sms_code_str = "%06d" % random.randint(0,999999)
    current_app.logger.info("短信验证码为%s" % sms_code_str)
    result = CCP().send_template_sms(mobile, [sms_code_str,constants.SMS_CODE_REDIS_EXPIRES / 60],1)

    if result !=0:
        return jsonify(errno=RET.THIRDERR, errmsg="短信验证码发送失败")
    try:
        redis_store.setex("SMS_" + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code_str)
    except Exception as e:
        current_app.__logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="手机验证码保存失败")

    # 7.给前段一个响应
    return jsonify(errno=RET.OK, errmsg="短信验证码发送成功")


@passport_blu.route("/image_code")
def get_image_code():
    """
    1.接受参数
    2.校验参数是否存在
    3.生成验证码 captcha
    4.把随机的字符串生成的文本验证码以key，value的形式保存到redis
    5.把图片验证码返回给浏览器
    :return:
    """
    # 1.接收参数
    image_code_id = request.args.get("imageCodeId")

    # 2.校验参数是否存在
    if not image_code_id:
        abort(404)
    # 3.
    _, text, image = captcha.generate_captcha()

    # 4. 把随机的字符串和生成的文本验证码以
    try:
        redis_store.setex("ImageCodeId_" + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"

    return response
