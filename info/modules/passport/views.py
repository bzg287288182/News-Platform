from flask import abort, request, current_app, make_response

from info import constants, redis_store
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha


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
