# coding:utf-8
# 配置worker
BROKER_URL = "redis://127.0.0.1:6379/5"
# 配置backend
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/6"
