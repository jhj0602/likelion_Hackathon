# server/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
# https://stackoverflow.com/questions/50336688/django-load-production-settings-for-celery
# set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
# server를 기준으로 Celery 실행

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
app = Celery('myproject')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
# should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

# 여기서 시간 조정하면 됨
# 일단 100초 마다로 설정 해뒀음
app.conf.beat_schedule = {
    'add-every-100-seconds': {
        'task': 'save_temp', # 여기서 이름 바꾸면 됨
        # 'task': 'save_lottedata' 이거 주석 풀고 위에꺼 주석하면 lotteproduct 함수 호출
        'schedule': 100.0,  # 100초마다
    },
}
