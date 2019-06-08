from flask import abort, request, current_app, make_response

from info import constants, redis_store
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha

# 1.请求的url
@passport_blu.route("/sms_code", methods=["POST"])
def get_sms_code():
    """

    :return:
    """




@passport_blu.route("/image_code")
def get_image_code():
    """
    1.接受参数
    2.校验参数是否存在
    3.生成验证码 captcha
    4.把随机的字符串生成的文本验证码以key，ｖａｌｕｅ的形式保存到redis
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
        redis_store.setex("ImageCodeId_" + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES ,text)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"

    return response

