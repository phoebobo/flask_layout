from flask import request, jsonify, session
import re
import logging

from . import api
from apps import redis_store, db
from apps.models import User
from apps import constant
from apps.utils.login_required import login_required


@api.route('/logout', methods=['DELETE'])
@login_required
def logout():
    session.pop('user_id')
    session.pop('user_phone')
    return jsonify(msg='user log out', errcode=constant.USER_NOT_LOGIN)


@api.route('/is_login')
@login_required
def index():
    user_id = session.get('user_id')
    user_phone = session.get('user_phone')
    return jsonify(msg_code=constant.RET_OK, user_id=user_id, user_phone=user_phone)


@api.route('/verify_code/', methods=['POST'])
def verify_code():
    # 验证手机号和验证码
    phone = request.form.get('phone')
    msg_code = request.form.get('msg_code')
    print(phone)
    # 校验参数是否为空
    if not all([phone, msg_code]):
        return jsonify(phone=phone, msg_code=msg_code, msg='有参数为空')
    # 校验手机号码是否合法
    if not re.match(r'1[3456789]\d{9}', phone):
        return jsonify(msg='手机号码不合法')
    # 校验验证码是否一致
    try:
        # 取到是bytes类型
        save_code = redis_store.get('msg_%s' % phone).decode()
        print(save_code)
        if save_code == msg_code:
            print('与本地一致')
        else:
            return jsonify(err_msg='msg_code error')
    except Exception as e:
        logging.error(e)
        return jsonify(msg='redis error')
    # 如果不存在则创建用户
    user_obj = User.query.filter_by(phone=phone).first()

    try:
        if user_obj:
            print('用户已存在')
        else:
            print('用户不存在则创建')
            user_obj = User(phone=phone)
            db.session.add(user_obj)
            db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(msg='mysql error')

    # 添加到session,也就是存在不存在都登录
    session['user_id'] = user_obj.id
    session['user_phone'] = phone
    # 响应
    return jsonify(msg='ok')

