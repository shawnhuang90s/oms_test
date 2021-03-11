[TOC]

### 定时任务

#### 1. 日志配置

```python
# oms_test/oms_conf/oms_log.py
......
# 定时任务路径配置
crontab_log = f'{log_base_path}/crontab/'
```

#### 2. 下载并添加 django-crontab

```bash
pip install django-crontab

# oms_test/oms_test/settings.py
INSTALLED_APPS = [
    ......
    
    # 第三方应用
    'django_crontab',

    # 自建应用
    'store.apps.StoreConfig',
    'user.apps.UserConfig',
    'basic.apps.BasicConfig',
]

......
# 
```

#### 3. 编写一个测试函数

```python
# oms_test/basic/tests.py
import loguru
from oms_test.settings import CRONTAB_LOG
logger = loguru.logger
logger.add(f'{CRONTAB_LOG}basic_tests.log', format='{time} {level} {message}', level='INFO')


def crontab_test():
    """测试定时任务"""
    logger.info(1111111111111111111)
    logger.info('这是定时任务测试...')
    logger.info(2222222222222222222)


if __name__ == '__main__':
    crontab_test()
```

#### 4. 配置定时任务

```python
# oms_test/oms_test/settings.py
......
# 定时任务配置
CRONJOBS = [
    # 每一分钟执行一次测试函数, 后面的参数从项目根目录开始
    # 比如这里相当于执行 oms_test/basic/tests 下的 crontab_test() 
    ('*/1 * * * *', 'basic.tests.crontab_test'),
]
```

#### 5. 执行定时任务

```bash
python manage.py crontab add
# 一分钟后，查看对应日志文件，发现有内容了，说明定时任务生效

# 查看有哪些定时任务
python manage.py crontab show
# 删除所有的定时任务(上面测试的定时任务生效后记得移除)
python manage.py crontab remove
```

### 获取项目所在服务器的 IP 地址

```python
# oms_test/utils/get_host_ip.py
import socket


def get_ip():
    """查询项目所在服务器的 IP 地址"""
    socket_obj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        socket_obj.connect(('8.8.8.8', 80))
        ip = socket_obj.getsockname()[0]
    finally:
        socket_obj.close()

    return ip


if __name__ == '__main__':
    r = get_ip()
    print(f"项目所在服务器的 IP 地址：{r}")
```

### Django 中 Celery 的使用

#### 1. Celery 基本概念

- 倘若一个用户在执行某些操作需要等待很久才返回，这大大降低了网站的吞吐量，而 Celery 可以解决这个问题
- Celery 是一个基于 python 开发的分布式任务队列，支持使用任务队列的方式在分布的机器/进程/线程上执行任务调度
- Django 的请求处理过程都是同步的无法实现异步任务，Celery 可以实现异步任务处理
- Django 请求过程简单说明：浏览器发起请求-->请求处理-->请求经过中间件-->路由映射-->视图处理业务逻辑-->响应请求
- 同步请求：所有逻辑处理、数据计算任务在View中处理完毕后返回 Response。在View处理任务时用户处于等待状态，直到页面返回结果
- 异步请求：View 中先返回 Response，再在后台处理任务。用户无需等待，可以继续浏览网站。当任务处理完成时，我们可以再告知用户
- Celery 采用典型的生产者-消费者模式，主要由三部分组成：broker（消息队列）、workers（消费者：处理任务）、backend（存储结果）
- 实际应用中，用户从 Web 前端发起一个请求，我们只需要将请求所要处理的任务丢入任务队列 broker 中，由空闲的 worker 去处理任务即可
- 处理的结果会暂存在后台数据库 backend 中，可以在一台机器或多台机器上同时起多个 worker 进程来实现分布式地并行处理任务
- 必须拥有一个 broker 消息队列用于发送和接收消息，Celery 官网给出了多个 broker 的备选方案：RabbitMQ、Redis、Database（不推荐）以及其他的消息中间件
- 高可用：当任务执行失败或执行过程中发生连接中断，Celery 会自动尝试重新执行任务
- 快速：一个单进程的 Celery 每分钟可处理上百万个任务

#### 2. 安装消息队列 RabbitMQ 服务和 Python 第三方包

```bash
# Celery的默认 broker 是 RabbitMQ
sudo apt-get install rabbitmq-server  # Ubuntu 系统
pip install celery
pip install django-celery
```

#### 3. 任务配置

```python
# oms_test/oms_test/celery.py
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


# oms_test/oms_test/settings.py
import djcelery
......
INSTALLED_APPS = [
    ......
    # 第三方应用
    'django_crontab',
    'djcelery',
    ......
]
......
# 任务队列 Celery 配置
djcelery.setup_loader()
BROKER_BACKEND = 'redis'
BROKER_URL = 'redis://127.0.0.1:6379/1'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2'
CELERY_ACCEPT_CONTENT = ['pickle', 'json', ]


# oms_test/oms_test/__init__.py
from __future__ import absolute_import, unicode_literals
import pymysql
from .celery import app as celery_app


pymysql.install_as_MySQLdb()
__all__ = ['celery_app']
```

1）当 djcelery.setup_loader() 运行时，Celery 便会去查看 INSTALLD_APPS 下包含的所有 app 目录中的 tasks.py 文件， 找到标记为 task 的方法，将它们注册为 celery  task

2）在 Django 中如果没有设置 backend，会使用其默认的后台数据库用来存储数据，注意此处 backend 的设置是通过关键字 CELERY_RESULT_BACKEND 来配置

3）与一般的 .py 文件中实现 Celery 的 backend 设置方式有所不同，一般的 .py 中是直接通过设置 backend 关键字来配置，如下所示： 

```Python
app = Celery('tasks', backend='amqp://guest@localhost//', broker='amqp://guest@localhost//')
```

#### 4. 启动 worker

```bash
celery worker -A oms_test -l info
# 也可以是：python manage.py celery worker -l info

# 如果报错如下，原因是 Python3.7 版本中 async 已经是一个关键字, 这个包的命名与其产生冲突
# 解决办法有两个：
# 1. 下载比 3.7 更低的版本的 Python
# 2. 将 kombu 下面的 async 目录重命名，比如 new_async，然后使用上面命令启动看哪里提示这种报错, 把 async 改为 new_async 即可
# 第二种方法相对麻烦，但因为 Python3.7 有 f'格式化属性{变量名}' 的用法，在项目中用了挺多地方的，如果下载低版本的 Python，使用 f 格式化的地方都要改过来更麻烦
 File "/home/yanfa/.virtualenvs/oms_test/lib/python3.7/site-packages/celery/utils/timer2.py", line 19
    from kombu.async.timer import Entry, Timer as Schedule, to_timestamp, logger
                   ^
SyntaxError: invalid syntax

# 修复问题后，再启动，没问题的话有如下信息：
 -------------- celery@yanfa-H110SD3-C v3.1.26.post2 (Cipater)
---- **** ----- 
--- * ***  * -- Linux-4.15.0-91-generic-x86_64-with-debian-stretch-sid
-- * - **** --- 
- ** ---------- [config]
- ** ---------- .> app:         oms_test:0x7f03ade0ff50
- ** ---------- .> transport:   redis://guest@localhost:6379//
- ** ---------- .> results:     redis://127.0.0.1:6379/2
- *** --- * --- .> concurrency: 4 (prefork)
-- ******* ---- 
--- ***** ----- [queues]
 -------------- .> celery           exchange=celery(direct) key=celery
                

[tasks]
  . oms_test.celery.debug_task

[2021-03-11 08:35:02,309: INFO/MainProcess] Connected to redis://guest@localhost:6379//
[2021-03-11 08:35:02,320: INFO/MainProcess] mingle: searching for neighbors
[2021-03-11 08:35:03,324: INFO/MainProcess] mingle: all alone
[2021-03-11 08:35:03,331: WARNING/MainProcess] celery@yanfa-H110SD3-C ready.


# 启动 beat 
celery beat -A oms_test -l info
# 或者这样：python manage.py celery beat -l info  
# 运行结果：
celery beat v3.1.26.post2 (Cipater) is starting.
__    -    ... __   -        _
Configuration ->
    . broker -> redis://guest@localhost:6379//
    . loader -> celery.loaders.app.AppLoader
    . scheduler -> celery.beat.PersistentScheduler
    . db -> celerybeat-schedule
    . logfile -> [stderr]@%INFO
    . maxinterval -> now (0s)
[2021-03-11 08:39:22,068: INFO/MainProcess] beat: Starting...
```

### excel 文件上传下载 与 Celery 配合使用

#### 1. 项目中新建 excel 上传下载目录

```bash
# oms_test/files/download/
# oms_test/files/upload/
```

#### 2. 配置文件添加路径

```python
# oms_test/oms_test/settings.py
......
# 文件上传与下载路径配置
UPLOAD_ROOT = os.path.join(BASE_DIR, 'files/upload/')
DOWNLOAD_ROOT = os.path.join(BASE_DIR, 'files/download/')
```

#### 3. 新增日志

```python
# oms_test/oms_conf/oms_log.py
......
# 文件上传下载日志配置
file_log = f'{log_base_path}/file/'

# oms_test/oms_test/settings.py
......
CRONTAB_LOG = oms_log.crontab_log
FILE_LOG = oms_log.file_log
......
```

#### 4. 处理 excel 文件内容

```python
# oms_test/basic/views.py

```



#### 1. 定义 excel 文件表头样式

```python
# oms_test/utils/excel_config.py
import xlwt


def set_excel_style(color='white', colour_index=0, height=180, bold=False, name=u'宋体',
                        horz=xlwt.Alignment.HORZ_CENTER, vert=xlwt.Alignment.VERT_CENTER):
    """定义 excel 文件内容样式"""
    style = xlwt.XFStyle()
    # 设置字体
    font_one = xlwt.Font()
    font_one.name = name
    font_one.bold = bold
    font_one.colour_index = colour_index
    font_one.height = height
    style.font = font_one

    # 设置文字位置
    alignment = xlwt.Alignment()
    alignment.horz = horz  # 水平方向设置：左对齐/居中/右对齐
    alignment.vert = vert  # 垂直方向设置
    style.alignment = alignment

    # 设置单元格背景颜色
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map[color]
    style.pattern = pattern

    # 设置单元格边框线条
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    style.borders = borders

    return style
```



