from __future__ import absolute_import, unicode_literals
from celery.decorators import task

from celery.schedules import crontab # 시간에 따른 호출을 위해
from .views import save_test

@task(name="save_temp")
def save_temp():
    
    return save_test()

@task(name="save_lottedata")
def save_lottedate():
    return lotteproduct()
