#! /usr/bin/env python3
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_wtf.csrf import generate_csrf


from apps import create_app, db


# 初始化app
app = create_app('dev')

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.after_request
def after_request(response):
    # 调用函数生成csrf token
    csrf_token = generate_csrf()
    # 设置cookie传给前端
    response.set_cookie('csrf_token', csrf_token)
    return response


if __name__ == '__main__':
    manager.run()
