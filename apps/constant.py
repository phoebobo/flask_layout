# 数据常量

# 短信验证码保存时间 单位　秒
PHONE_CODE_REDIS_EXPIRES = 60*5
# 手机不能重复发送的时间
PHONE_FLAG_REDIS_EXPIRES = 60*3
# redis存储车辆信息过期时间
CAR_INFO_REDIS_EXPIRES = 60*60*24

# 返回的状态码
USER_NOT_LOGIN = 4001,  # 未登录
RET_OK = 0,  # 没有报错
RET_IMAGE_CODE = 4002,  # 前端获取图片错误
RET_IMAGE_FULL = 4003,  # 车辆数据库超过３０
RET_IMAGE_DBERR = 4005,  # 存储进车辆图片数据库出错
RET_CAR_NOTFOUND = 4004,  # 没找到车辆
RET_REDIS_INSERT_ERR = 4006  # REDIS数据插入错误
RET_REDIS_OUTPUT_ERR = 4007  # REDIS数据取出错误
DB_COMMIT_ERR = 4008  # 数据库存储出错

# 七牛存储空间　cars
QINIUURL = 'http://puger6n16.bkt.clouddn.com/'

