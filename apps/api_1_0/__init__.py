# cars_flask/cars/api_1_0/__init__.py
from flask import Blueprint


# 创建蓝图，取名和模块名
api = Blueprint('api_1_0', __name__)

# 要写在下面防止循环导入
from . import user, verify, cars
