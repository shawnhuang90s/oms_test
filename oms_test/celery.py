from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oms_test.settings')

app = Celery('oms_test', broker='amqp://guest@localhost//')
app.conf.ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': {
        'url': 'redis://127.0.0.1:6379/1',
        'default_timeout': 60 * 60
    }
}

# 在这里使用字符串意味着 worker 不必序列化子进程的配置对象
# 如果使用 namespace='CELERY' 表示所有与 Celery 相关的配置都要有 CELERY_ 这个前缀
# app.config_from_object('django.conf:settings', namespace='CELERY')
app.config_from_object('django.conf:settings')

# 从所有已经注册的 app 子应用下加载任务模块, 简单的说, 会自动加载类似 oms_test/store/tasks.py 这个文件
# app.autodiscover_tasks()  # 自动加载每个 app 下的 tasks.py
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request}')
