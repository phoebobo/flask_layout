from datetime import datetime
# 模型类

from . import db
from apps.constant import QINIUURL


class BaseModel(object):
    id = db.Column(db.Integer, primary_key=True)
    is_delete = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


registrations = db.Table("registrations", db.Column("sc_user_id", db.Integer, db.ForeignKey("sc_users.id")),
                         db.Column("sc_car_id", db.Integer, db.ForeignKey("sc_cars_info.id"))
                         )


class User(BaseModel, db.Model):
    __tablename__ = 'sc_users'
    name = db.Column(db.String(20), unique=True, nullable=True)
    # 密码需要加密,长度需要长
    password = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(11), nullable=False)
    id_number = db.Column(db.String(18), nullable=True)
    # 有几个外键关系
    # apps = db.relationship('Car', backref='user')
    order = db.relationship('Order', backref='user')
    # 多对多关系
    cars = db.relationship("Car",
                           secondary=registrations,
                           backref=db.backref("user_set", lazy="dynamic"))

    def __repr__(self):
        return self.name


class Car(BaseModel, db.Model):
    __tablename__ = 'sc_cars_info'
    # 车信息name是显示
    car_number = db.Column(db.String(50), autoincrement=True)  # 车架号
    price = db.Column(db.Float, default=100000)  # 价格
    car_age = db.Column(db.Integer, default=1)  # 车龄
    car_type = db.Column(db.String(10), default=4)  # 车型，几厢
    car_gearbox = db.Column(db.Integer, default=1)  # 变速箱0手动，1自动
    car_distance = db.Column(db.String(10), default='1000')  # 里程数
    car_displacement = db.Column(db.String(10), nullable=True)  # 排量
    car_register_time = db.Column(db.DateTime, nullable=True)  # 上牌时间
    car_color = db.Column(db.String(10), default='白色')  # 车颜色
    car_oil_type = db.Column(db.String(10), default='92')  # 车燃油
    annual_datetime = db.Column(db.String(10), nullable=True)  # 年检日期 暂定为显示时间
    compulsory_datetime = db.Column(db.String(10), nullable=True)  # 交强险日期
    commercial_datetime = db.Column(db.String(10), nullable=True)  # 商业险日期
    seat_num = db.Column(db.Integer, default=4)  # 座位个数
    transfer_times = db.Column(db.Integer, default=0)  # 过户次数
    emission_standard = db.Column(db.String(10), default='0')  # 车排放标准
    # 配置默认图片
    index_image_url = db.Column(db.String(100), nullable=True)
    # 外键,分别指的是车的拥有者，品牌，车
    # user_id = db.Column(db.Integer, db.ForeignKey('sc_users.id'))
    brande_id = db.Column(db.Integer, db.ForeignKey('sc_cars_brande.id'))
    model_id = db.Column(db.Integer, db.ForeignKey('sc_cars_model.id'))
    # 关联图片，基础信息表，发动机，底盘
    images = db.relationship('CarImage', backref='apps')
    base_info = db.relationship('BaseInfo', backref='apps')
    motor_param = db.relationship('MotorParameter', backref='apps')
    chassis = db.relationship('Chassis', backref='apps')
    # 订单
    orders = db.relationship('Order', backref='apps')
    # 关联user
    users = db.relationship('User', secondary=registrations,
                            backref=db.backref('cars_set'), lazy='dynamic')

    def to_list_dict(self):
        # 返回列表页的数据
        # 需要的数据:品牌，模型 detail
        # 价格，年份，公里数  id  默认图片
        car_obj_dict = {
            'brand': self.brande.name,
            'model': self.model.name,
            'detail': self.model.detail,
            'price': self.price,
            'car_register_time': self.annual_datetime,
            'car_distance': self.car_distance,
            'car_id': self.id,
            # 默认图片
            'index_image_url': QINIUURL+self.index_image_url
        }
        return car_obj_dict

    def to_detail_dict(self):
        car_detail_dict = {
            'base_info': self.base_info[0].brand_model
        }
        return car_detail_dict


class Brande(BaseModel, db.Model):
    __tablename__ = 'sc_cars_brande'
    # 车品牌名
    name = db.Column(db.String(20), nullable=False)
    # 关联车
    cars = db.relationship('Car', backref='brande')
    models = db.relationship('CarModel', backref='brande')

    def __repr__(self):
        return self.name


class CarModel(BaseModel, db.Model):
    __tablename__ = 'sc_cars_model'
    # 这个是品牌类型表 比如帕萨特
    name = db.Column(db.String(20), nullable=False)
    detail = db.Column(db.String(150), nullable=True)
    # 外键
    brande_id = db.Column(db.Integer, db.ForeignKey('sc_cars_brande.id'))
    # 关系
    cars = db.relationship('Car', backref='model')

    def __repr__(self):
        return self.name


class CarImage(BaseModel, db.Model):
    __tablename__ = 'sc_cars_image'
    url = db.Column(db.String(100))  # 图片路径

    car_id = db.Column(db.Integer, db.ForeignKey('sc_cars_info.id'))


class Order(BaseModel, db.Model):
    __tablename__ = 'sc_orders'
    car_price = db.Column(db.Float, nullable=True)  # 车价格
    car_charge = db.Column(db.Float, nullable=True)  # 手续费
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('sc_users.id'))
    car_id = db.Column(db.Integer, db.ForeignKey('sc_cars_info.id'))


# 车的详细信息，６个表
class BaseInfo(db.Model):
    # 基础信息表
    __tablename__ = 'sc_cars_baseinfo'
    id = db.Column(db.Integer, primary_key=True)
    brand_model = db.Column(db.String(20), nullable=True)  # 证件品牌号
    trade_name = db.Column(db.String(20), nullable=True)  # 厂商
    car_grade = db.Column(db.String(20), nullable=True)  # 级别
    car_engine = db.Column(db.String(20), nullable=True)  # 发动机
    car_gearbox = db.Column(db.String(20), nullable=True)  # 变速箱
    body_structure = db.Column(db.String(20), nullable=True)  # 车身结构
    length_detail = db.Column(db.String(20), nullable=True)  # 长宽高
    wheel_base = db.Column(db.String(20), nullable=True)  # 轴距
    volume_luggage = db.Column(db.String(20), nullable=True)  # 行李箱容积
    curb_weight = db.Column(db.String(20), nullable=True)  # 整备质量
    # 外键
    car_id = db.Column(db.Integer, db.ForeignKey('sc_cars_info.id'))


class MotorParameter(db.Model):
    # 发动机参数
    __tablename__ = 'sc_cars_motorparameter'
    id = db.Column(db.Integer, primary_key=True)
    displacement = db.Column(db.String(10))  # 排量
    suction_type = db.Column(db.String(10))  # 进气形式
    cylinder = db.Column(db.String(10))  # 气缸
    max_horsepower = db.Column(db.String(10))  # 最大马力(Ps)
    max_torque = db.Column(db.String(10))  # 最大扭矩(N*m)
    car_oil_type = db.Column(db.String(10))  # 燃料类型
    ROZ = db.Column(db.String(10))  # 燃油标号
    Oilsupplyway = db.Column(db.String(10))  # 供油方式
    emission_standard = db.Column(db.String(10))  #　排放标准
    car_id = db.Column(db.Integer, db.ForeignKey('sc_cars_info.id'))  # 车


class Chassis(db.Model):
    '''底盘及制动'''
    __tablename__ = 'sc_chassis'
    id = db.Column(db.Integer, primary_key=True)  # id
    drive_mode = db.Column(db.String(20))  # 驱动方式
    front_suspension_type = db.Column(db.String(20))  # 前悬挂类型

    rear_suspension_type = db.Column(db.String(20))  # 后悬挂挂类型
    front_brake_type = db.Column(db.String(20))  # 前制动类型
    rear_brake_type = db.Column(db.String(20))  # 后制动类型
    parking_brake_type = db.Column(db.String(20))  # 驻车制动类型
    front_tire_specification = db.Column(db.String(20))  # 前轮胎规格
    rear_tire_specification = db.Column(db.String(20))  # 后轮胎规格

    car_id = db.Column(db.Integer, db.ForeignKey('sc_cars_info.id'))
