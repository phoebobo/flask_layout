# 认证
from flask import request, jsonify
import re
import random
import logging

from . import api
from apps import redis_store
from apps.libs.CCPRestSDK.sms import CCP
from apps import constant


# @api.route('/login')
# def login():
#     return render_template('login.html')


@api.route('/msg_code/', methods=['POST', ])
def send_msg_code():
    # 获取参数
    print('#######################')
    phone = request.form.get('phone')
    print(phone)
    # 校验参数是否为空
    if not all([phone]):
        return jsonify(phone=phone, msg='有参数为空')
    # 校验手机号码是否合法
    if not re.match(r'1[3456789]\d{9}', phone):
        return jsonify(msg='手机号码不合法')
    # 生成并存储短信验证码
    msg_code = '%04d' % random.randint(0, 9999)
    print(msg_code)
    # 参数是key,value,过期时间
    try:
        redis_store.set('msg_%s' % phone, msg_code, constant.PHONE_CODE_REDIS_EXPIRES)
    except Exception as e:
        logging.error(e)
        return jsonify(msg='验证码保存错误')
    logging.debug(msg_code)
    # 发送短信验证码
    ccp = CCP()
    ret = ccp.send_template_sms(phone, [msg_code, constant.PHONE_CODE_REDIS_EXPIRES/60], '1')
    print('手机验证码发送结果', ret)
    if ret == -1:
        return '发送失败'
    # 响应
    return jsonify(msg=constant.RET_OK)




