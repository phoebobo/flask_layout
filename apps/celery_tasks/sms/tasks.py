from celery import Celery

app = Celery('apps', broker="redis://127.0.0.1:6379/5")


@app.task()
def printlog():
    print('#########################')
    print('celery')
