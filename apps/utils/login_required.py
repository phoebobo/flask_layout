import functools
from flask import session, jsonify, g

from apps import constant
# 登录验证装饰器


def login_required(func):

    # 修饰内层函数，防止当前装饰器去修改被装饰函数的__name__属性
    @functools.wraps(func)
    def inner(*args, **kwargs):
        user_id = session.get('user_id')
        print(session.get('user_phone'))
        print('装饰器', user_id)
        if not user_id:
            return jsonify(err_msg='user not log in', errcode=constant.USER_NOT_LOGIN)
        else:
            g.user_id = user_id
            return func(*args, **kwargs)
    return inner

