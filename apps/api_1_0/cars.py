from . import api
from flask import request, jsonify, session
from apps.utils.file_upload import upload_file_qiniu
import json

from apps import constant
from apps.models import CarImage, Car, Brande, User
from apps import db, redis_store
from apps.utils.login_required import login_required

@api.route('/upload_file', methods=['POST'])
def upload_car_img():
    # 表单数据，需要img图片文件，car_id车id
    try:
        # 表单的file文件转bytes类型
        data = request.files.get('img').read()
        print(type(request.files.get('img')))
    except Exception as e:
        print(e)
        return jsonify(errcode=constant.RET_IMAGE_CODE, errmsg='获取图片出错')

    try:
        # 获取车辆id,校验id
        car_id = request.form.get('car_id')
        car_obj = Car.query.filter_by(id=car_id).first()
        if car_obj:
            # 上传图片
            url_img = upload_file_qiniu(data)
            # todo 判断当前表中，图片不超过３０个
            ret = CarImage.query.filter_by(car_id=car_id)
            print(url_img)
            if ret.count() >= 30:
                return jsonify(errcode=constant.RET_IMAGE_FULL, errmsg='车辆图片保存超过３０个')
            # 修改价格
            car_obj.price = request.form.get('price')

            # todo 将我们的图片地址保存到图片表
            try:
                car_img = CarImage(url=url_img, car_id=car_id)
                db.session.add(car_img)
                db.session.commit()
            except Exception as e:
                print(e)
                db.session.rollback()
                return jsonify(errcode=constant.RET_IMAGE_DBERR, errmsg='存储进car_img数据库出错')
        else:
            return jsonify(errcode=constant.RET_CAR_NOTFOUND, errmsg='车辆不存在')
    except Exception as e:
        print(e)
        return jsonify(errcode=constant.RET_IMAGE_CODE, errmsg='上传图片出错')

    return jsonify(code=constant.RET_OK, msg=url_img)


@api.route('/apps')
def cars_list_info():
    # 将是一个get请求，返回车辆列表
    # 有可能为空
    brand = request.args.get('brand')
    car_model = request.args.get('model')
    print(request.args.get('price'))

    if len(brand) == 0 and len(car_model) == 0:
        cars_lists = Car.query.all()
        print(cars_lists)
        ret_data_list = []
        for each in cars_lists:
            # 调用对象的方法来实现转dict
            ret = each.to_list_dict()
            print(ret)
            # 添加进字典
            ret_data_list.append(ret)
        print(ret_data_list)
        return jsonify(data=ret_data_list)

    elif len(brand) == 0 and len(car_model) !=0:
        # 只有型号没有品牌
        car_lists = Car.query.all()
        ret_data_list = []  # todo 需要返回的数据
        for each in car_lists:
            if each.brande.car_model == car_model:
                print(car_model)

        return jsonify(data=ret_data_list)

    elif len(brand) != 0 and len(car_model) ==0:
        # 只有品牌
        brand_id = Brande.query.filter_by(name=brand).first().id
        cars_lists = Car.query.filter_by(brande_id=brand_id).all()
        ret_data_list = []  # todo 需要返回的数据
        for each in cars_lists:
            # 调用对象的方法来实现转dict
            ret = each.to_list_dict()
            print(ret)
            # 添加进字典
            ret_data_list.append(ret)
        return jsonify(data=ret_data_list)

    return jsonify(msg='ok')


@api.route('/car_detail')
def cat_detail():
    # 这个是详情页,只需要获取car_id
    car_id = request.args.get('car_id')
    car_obj = Car.query.get(car_id)
    # 检验数据是否为空
    if not car_obj:
        return jsonify(errcode=constant.RET_CAR_NOTFOUND, errmsg='car_id出错')
    # todo 当用户登录的情况下，存储car_id到redis数据库8中，类型用列表，有个g变量存了user_id
    user_id = session.get('user_id')
    if user_id:
        try:
            history_key = 'history_%s' % user_id
            # 可能插入重复，所以要删除原来的再加入
            redis_store.lrem(history_key, 0, car_id)
            # 进行存储,左插入，获取使用lrange
            redis_store.lpush(history_key, car_id)
        except Exception as e:
            print(e)
            return jsonify(errcode=constant.RET_REDIS_INSERT_ERR, errmsg='redis插入错误')

    print(request.args)
    print(car_obj)  # todo 获取到了这辆车，然后展示六个表内容和图片，to_detail_dict()
    # todo 防止频繁访问mysql，存进redis
    redis_key = 'mysql-redis_%s' % car_id  # 存进redis的key名
    redis_data = redis_store.get(redis_key)
    if redis_data:
        # 注意bytes转码
        ret_dict = redis_data.decode()
    else:
        # 字典存进redis要序列化
        try:
            ret_dict = json.dumps(car_obj.to_detail_dict())
            redis_store.set(redis_key, ret_dict, constant.CAR_INFO_REDIS_EXPIRES)
        except Exception as e:
            print(e)
            return jsonify(errcode=constant.RET_REDIS_INSERT_ERR, errmsg='redis插入错误')
    # 返回信息，和data
    ret_dict = json.loads(ret_dict)
    return jsonify(msg='ok', data=ret_dict)


@api.route('/userhistory')
@login_required
def user_history():
    # 用户的浏览记录，放在redis中存储,打开车辆详情页就存储，用户登录才保存
    user_id = session.get('user_id')
    user_obj = User.query.get(user_id)
    user_phone = user_obj.phone
    # 判断非空
    if not user_obj:
        return jsonify(msg='用户不存在', code=constant.USER_NOT_LOGIN)
    history_key = 'history_%s' % user_id

    # 判断redis是否存在数据
    redis_data = redis_store.lrange(history_key, 0, -1)
    if redis_data:
        ret_list = []
        try:
            for car_id in redis_data:
                # 取出来是Bytes类型
                car_id = car_id.decode()
                print(car_id)
                car_obj = Car.query.get(car_id)
                ret_list.append(car_obj.to_list_dict())
            return jsonify(code=constant.RET_OK, data=ret_list, user_phone=user_phone)
        except Exception as e:
            return jsonify(msg='redis数据库出错', code=constant.RET_REDIS_OUTPUT_ERR)
    return jsonify(msg='null', code=constant.RET_CAR_NOTFOUND)


@api.route('/collect')
@login_required
def collect_cars():
    # todo 收藏车，根据get发送的carid
    car_id = request.args.get('car_id')
    car_obj = Car.query.get(car_id)
    # 分别获取car和user对象，收藏是车对用户，1对多
    user_id = session.get('user_id')
    user_obj = User.query.get(user_id)

    # 判断非空
    if not all([car_obj, user_obj]):
        return jsonify(msg='用户不存在', code=constant.USER_NOT_LOGIN)
    try:
        print('car_obj.users')
        # 这是收藏车
        car_obj.users.append(user_obj)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(msg='db数据库出错', code=constant.DB_COMMIT_ERR)

    return jsonify(msg='ok', code=constant.RET_OK)


@api.route('/show_collect')
@login_required
def show_collect():
    # 收藏数据，是多对多关系
    user_id = session.get('user_id')
    user_obj = User.query.get(user_id)
    user_phone = user_obj.phone
    # 判断非空
    if not user_obj:
        return jsonify(msg='用户不存在', code=constant.USER_NOT_LOGIN)

    # print(user_obj.apps)
    # 如果收藏为空则返回msg=null
    if not len(user_obj.cars):
        return jsonify(msg='null', code=constant.RET_CAR_NOTFOUND)
    # 返回的数据列表
    ret_list = []
    for car_obj in user_obj.cars:
        ret_list.append(car_obj.to_list_dict())
    return jsonify(code=constant.RET_OK, data=ret_list, user_phone=user_phone)
