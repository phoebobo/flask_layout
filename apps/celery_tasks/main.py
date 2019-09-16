from celery import Celery


app = Celery('apps')

app.config_from_object('apps.celery_tasks.config')
app.autodiscover_tasks(['apps.celery_tasks.sms'])
