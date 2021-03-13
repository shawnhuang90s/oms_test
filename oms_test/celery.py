import os
from celery import Celery

# 设置 Celery 执行时的默认环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oms_test.settings')

# 获取一个 Celery 实例对象
app = Celery('oms_test')

# 任务去重配置
app.conf.ONCE = {
  'backend': 'celery_once.backends.Redis',
  'settings': {
    'url': 'redis://127.0.0.1:6379/0',
    'default_timeout': 60 * 60
  }
}

# 将 Django 设置模块添加为 Celery 的配置源
# 这意味着不必使用多个配置文件, 而直接从 Django 设置中配置 Celery
# namespace 意味着所有 Celery配置选项 必须以大写而不是小写指定, 并以 CELERY_ 开头
app.config_from_object('django.conf:settings', namespace='CELERY')

# 从所有已经注册的 app 子应用下加载任务模块, 简单的说, 会自动加载类似 oms_test/store/tasks.py 这个文件
app.autodiscover_tasks()  # 自动加载每个 app 下的 tasks.py


@app.task(bind=True)
def debug_task(self):
    """转储请求信息"""
    print(f'Request: {self.request!r}')
