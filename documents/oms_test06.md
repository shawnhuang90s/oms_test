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

> 参考文档：https://docs.celeryproject.org/en/stable/index.html

#### 2. 安装 RabbitMQ 和第三方包

```bash
sudo apt-get install rabbitmq-server
pip install celery
```

#### 3. 项目根目录新建 tasks.py 文件

```python
# oms_test/tasks.py
from celery import Celery


app = Celery('tasks', broker='pyamqp://guest@localhost//')


@app.task
def add(x, y):
    return x + y
```

#### 4. 启动 Celery Worker 服务器

```bash
celery -A tasks worker --loglevel=INFO
# 运行结果示例：
 
 -------------- celery@yanfa-H110SD3-C v5.0.5 (singularity)
--- ***** ----- 
-- ******* ---- Linux-4.15.0-91-generic-x86_64-with-debian-stretch-sid 2021-03-12 18:04:01
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         tasks:0x7f79604fae10
- ** ---------- .> transport:   amqp://guest:**@localhost:5672//
- ** ---------- .> results:     disabled://
- *** --- * --- .> concurrency: 4 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery
                

[tasks]
  . tasks.add  # 注意这里有刚才我们新增的队列任务

[2021-03-12 18:04:02,049: INFO/MainProcess] Connected to amqp://guest:**@127.0.0.1:5672//
[2021-03-12 18:04:02,056: INFO/MainProcess] mingle: searching for neighbors
[2021-03-12 18:04:03,096: INFO/MainProcess] mingle: all alone
[2021-03-12 18:04:03,128: INFO/MainProcess] celery@yanfa-H110SD3-C ready.
```

#### 5. 进入 shell 中调度任务

```python
# 注意：在 Pycharm 中刚才我们已经打开了一个窗口启动 Celery Worker 服务器，现在我们先不动这个窗口，打开另一个窗口
python manage.py shell
# 运行示例：
In [1]: from tasks import add

In [2]: add.delay(1, 2)
# 调用任务将返回一个 AsyncResult 实例
# 这可用于检查任务的状态，等待任务完成或获取其返回值（或者如果任务失败，则获取异常和回溯）
Out[2]: <AsyncResult: 728ba3b0-5553-4205-b34b-b51aeb4f81ae>  

# 此时回到第一个窗口，发现多了两条日志信息，其中 728ba3b0-5553-4205-b34b-b51aeb4f81ae 是任务 ID，而最后的 3 是运行上面函数的结果
[2021-03-12 18:10:48,259: INFO/MainProcess] Received task: tasks.add[728ba3b0-5553-4205-b34b-b51aeb4f81ae]  
[2021-03-12 18:10:48,261: INFO/ForkPoolWorker-2] Task tasks.add[728ba3b0-5553-4205-b34b-b51aeb4f81ae] succeeded in 0.000429260002420051s: 3
```

#### 6. 保存结果

- 默认情况下不启用结果，为了执行远程过程调用或跟踪数据库中的任务结果，需要配置 Celery
- 有多个内置结果后端可供选择：[SQLAlchemy](http://www.sqlalchemy.org/) / [Django](http://djangoproject.com/) ORM， [MongoDB](http://www.mongodb.org/)，[Memcached](http://memcached.org/)，[Redis](https://redis.io/)，[RPC](https://docs.celeryproject.org/en/stable/userguide/configuration.html#conf-rpc-result-backend)（[RabbitMQ](http://www.rabbitmq.com/) / AMQP）
- 这里的示例中，使用 Redis 作为结果后端，但仍然使用 RabbitMQ 作为消息代理（一种流行的组合）

```python
# oms_test/tasks.py
.......
# 使用 Redis 的 0 号库来存储任务结果
app = Celery('tasks', backend='redis://localhost/0', broker='pyamqp://guest@localhost//')
......

# 退出 shell, 再重新进入
In [1]: from tasks import add

In [2]: ret = add.delay(2, 3)

In [3]: ret.ready()  # 查看任务是否已完成处理
Out[3]: False
```

#### 7. 项目中定义 Celery 实例

```python
# oms_test/oms_test/celery.py
import os
from celery import Celery

# 设置 Celery 执行时的默认环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oms_test.settings')
# 获取一个 Celery 实例对象
app = Celery('oms_test')
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
```

#### 8. 导入到项目模块中

```python
# oms_test/oms_test/__init__.py
import pymysql
from .celery import app as celery_app


pymysql.install_as_MySQLdb()
__all__ = ('celery_app',)
```

#### 9. 项目配置文件配置 Celery

```python
# oms_test/oms_test/settings.py
......
# Celery 配置
CELERY_TIMEZONE = "Asia/Shanghai"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
```

#### 10. 使用 Django 数据库缓存结果

```python
# 下载第三方包
pip install django-celery-results

# oms_test/oms_test/settings.py
......
INSTALLED_APPS = [
    ......
    # 第三方应用
    'django_crontab',
    'django_celery_results',
    ......
]
......
# Celery 配置
CELERY_TIMEZONE = "Asia/Shanghai"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_BACKEND = 'django-db'
.......


# 执行数据库迁移来创建 Celery 数据库表
python manage.py migrate django_celery_results
```

#### 11. 注意一个小细节

```python
# 前面已经配置了 Celery 在项目中的使用, 注意：app.autodiscover_tasks() 是寻找每个已经注册的 app 下面的 tasks.py 文件
# 所以现在执行之前根目录下的 tasks.py 文件，会报错
# 先启动 Celery Worker 服务器
celery -A oms_test worker -l info

# 打开另一个窗口，进入 shell 中
python manage.py shell
In [1]: from tasks import add

In [2]: add.delay(2, 2)
Out[2]: <AsyncResult: 05e8691c-1558-4ee3-a02f-d9ef412258c9>

# 打开刚才启动 Celery Worker 服务器的窗口，发现报错了，提示：
[tasks]  # 这里 tasks 列表里没有根目录下 tasks.py 中的 add() , 所以会报错
  . oms_test.celery.debug_task  

[2021-03-13 01:44:07,862: INFO/MainProcess] Connected to amqp://guest:**@127.0.0.1:5672//
[2021-03-13 01:44:07,870: INFO/MainProcess] mingle: searching for neighbors
[2021-03-13 01:44:08,890: INFO/MainProcess] mingle: all alone
[2021-03-13 01:44:08,923: INFO/MainProcess] celery@yanfa-H110SD3-C ready.

[2021-03-13 01:44:13,400: ERROR/MainProcess] Received unregistered task of type 'tasks.add'.
The message has been ignored and discarded.

Did you remember to import the module containing this task?
Or maybe you're using relative imports?

Please see
http://docs.celeryq.org/en/latest/internals/protocol.html
for more information.

The full contents of the message body was:
'[[2, 2], {}, {"callbacks": null, "errbacks": null, "chain": null, "chord": null}]' (81b)
Traceback (most recent call last):
  File "/home/yanfa/.virtualenvs/oms_test/lib/python3.7/site-packages/celery/worker/consumer/consumer.py", line 555, in on_task_received
    strategy = strategies[type_]
KeyError: 'tasks.add'

# 解决办法：项目配置文件中将具有 Celery 的任务的模块添加到 CELERY_IMPOTS 中
# oms_test/oms_test/settings.py
......
# Celery 配置
CELERY_TIMEZONE = "Asia/Shanghai"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_BACKEND = 'django-db'
CELERY_IMPORTS = (
    'tasks',  # 导入根目录下 tasks.py 文件
)
.......

# 重启，在 shell 中再次执行, 发现 tasks 列表中有了
......
[tasks]
  . oms_test.celery.debug_task
  . tasks.add
......
```

#### 12. .delay() 与 .apply_async() 的联系与区别

```python
# 不加参数的情况下，.delay() 相当于 .apply_async() 的快捷方式
python manage.py shell
In [1]: from tasks import add

In [2]: add.delay(2, 2)
Out[2]: <AsyncResult: 05e8691c-1558-4ee3-a02f-d9ef412258c9>

In [3]: add.apply_async((2, 2))
Out[3]: <AsyncResult: 004212b5-5fcb-4894-99ea-75243d6704aa>

        
# .apply_async() 可以指定发送的队列、设置任务最早在消息发送后的多久内执行
In [4]: add.apply_async((3, 4), countdown=2)
Out[4]: <AsyncResult: 9899aa7a-eeee-48b4-986f-56c19883b0de>

# 回到启动服务器的端口，仔细看日志信息：
......
[2021-03-13 02:05:21,118: INFO/MainProcess] Received task: tasks.add[079821e0-266f-4665-9c72-ac87b5641f14]  ETA:[2021-03-13 02:05:23.085097+00:00] 
# 注意：下面的信息 2s 后才出现
[2021-03-13 02:05:24,788: INFO/ForkPoolWorker-2] Task tasks.add[079821e0-266f-4665-9c72-ac87b5641f14] succeeded in 0.06239675200004058s: 7
```

#### 13. 获取任务的 ID

```python
# 还是在刚才的 shell 中
In [5]: r = add.delay(1, 99)

In [6]: r.id
Out[6]: '4312da5b-5897-4115-824c-1c785e13cbb1'
```

#### 14. 使用 celery_once 包对 Redis 加锁

- 目前还会出现一种情况，那就是相同的任务在不同的 worker 中可能会被重复执行
- 现在我们使用 Redis 作为 Broker，要想避免这种情况，有两种解决方案
- 一种是在执行任务的时候加上 Redis 分布式锁
- 一种是使用 celery_once 包，其实也是利用 Redis 加锁的原理，对任务去重

```python
# 安装第三方包
pip install -U celery_once

# Celery 配置新增内容：oms_test/oms_test/celery.py
......
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
......

# 后续执行任务时，使用 .apply_async(args=()) 的方式
```

#### 15. 每次重启项目后，异步任务也要重新启动

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

#### 4. 新建子应用并注册

```python
python manage.py startapp celery_tasks

# oms_test/oms_test/settings.py
......
INSTALLED_APPS = [
    ......
    # 自建应用
    'store.apps.StoreConfig',
    'user.apps.UserConfig',
    'basic.apps.BasicConfig',
    'celery_tasks.apps.CeleryTasksConfig',
]
......

# oms_test/oms_test/urls.py
......
urlpatterns = [
    path('', clock_show),
    path('store/', include(('store.urls', 'store'), namespace='store')),
    path('user/', include(('user.urls', 'user'), namespace='user')),
    path('basic/', include(('basic.urls', 'basic'), namespace='basic')),
    path('celery_tasks/', include(('celery_tasks.urls', 'basic'), namespace='celery_tasks')),
    re_path('api_doc/(?P<path>.*)', serve, {'document_root': API_DOC_ROOT}),
]
......
```

#### 5. 视图处理

```python
# 项目中新建处理任务队列的目录：oms_test/oms_test/celery_tasks
# 新建一个 excel 文件，命名为："测试模板文件", 注意后缀必须是 .xls (后面要用到，空文件就行)，并将其放到 oms_test/files/download/ 下
# oms_test/celery_taks/views.py
import os
import loguru
from .tasks import celery_test
from django.db import connection
from django.http import FileResponse
from rest_framework.views import APIView
from utils.get_username import get_username
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from oms_test.settings import FILE_LOG, UPLOAD_ROOT, DOWNLOAD_ROOT
from utils.decorator_func import admin_auth, login_auth, permission_auth
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_206_PARTIAL_CONTENT, HTTP_202_ACCEPTED
logger = loguru.logger
logger.add(f'{FILE_LOG}test.log', format='{time} {level} {message}', level='INFO')


class DealExcelInfoView(APIView):
    """使用分布式队列处理 excel 文件示例"""

    # @method_decorator(login_auth)
    def get(self, request):
        """下载模板或excel处理结果接口"""
        # username = get_username(request)
        username = 'admin'
        file_name = request.query_params.get("file_name", None)
        # task_id 作为标识符判断文件是否还在处理或是否已下载
        task_id = request.query_params.get("task_id", None)
        file_path = os.path.join(DOWNLOAD_ROOT, file_name)
        try:
            # 用户上传 excel 文件后, 服务器处理该文件, 并且返回一个 task_id 给前端
            # 用户点击下载处理结果时, 前端会将 task_id 再返回给后端
            # 我们之前已经安装了 django_celery_results 包, 这样可以根据 task_id 去查对应的任务是否已经处理完成
            if task_id:
                # 去数据库查询对应任务id的执行结果; 如果没查到说明任务尚未执行完
                cursor = connection.cursor()
                sql = f"SELECT result FROM django_celery_results_taskresult WHERE task_id={task_id};"
                cursor.execute(sql)
                result = cursor.fetchone()
                # 如果用户点击下载处理结果, 服务器还没有该文件, 而且任务表查不到任务的结果, 说明该文件还在处理中
                if not (os.path.exists(file_path) and result):
                    data = {'code': 0, 'desc': '您上传的 excel 还在处理中, 请稍后再下载处理结果'}
                    return Response(data, status=HTTP_204_NO_CONTENT)
                # 如果用户点击下载处理结果, 服务器还没有该文件, 但是任务表能找到对应任务的结果, 说明该文件已经处理完
                # 并且用户之前已经下载过处理结果了, 而我们要做的是用户第一次下载结果后就会在服务器删除该文件, 用户不能再次下载
                elif not os.path.exists(file_path) and result:
                    data = {'code': 0, 'desc': '您已下载过处理结果, 服务器已删除该文件'}
                    return Response(data, status=HTTP_206_PARTIAL_CONTENT)
            # 如果前端没有传 task_id, 有两种情况：
            # 1. 用户点击的是下载模板文件
            # 2. 用户之前已经下载过处理结果, 再次点击时应该提示已经下载过了
            # 当然, 也可以把下载模板文件和处理结果文件分两个接口来处理
            else:
                if not os.path.exists(file_path):
                    data = {'code': 0, 'desc': '模板文件未找到, 或您已下载过处理结果'}
                    return Response(data, status=HTTP_202_ACCEPTED)

            # 用户下载模板或处理结果正常时的处理
            response = FileResponse(open(file_path, "rb"))
            # response 标识该返回内容为文件格式
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment;filename={file_name}'
            # 模板文件在服务器中一直保留, 但是处理结果文件一旦下载就删除
            if file_name != "测试模板文件.xls" and os.path.exists(file_path):
                os.remove(file_path)
            return response
        except Exception as e:
            logger.info(f"用户：{username} 下载模板或处理结果时报错：{e}")
            data = {'code': 0, 'desc': f'下载模板文件或处理结果失败：{e}'}
            return Response(data)

    # @method_decorator(permission_auth)
    # @method_decorator(admin_auth)
    # @method_decorator(login_auth)
    def post(self, request):
        try:
            # username = get_username(request)
            username = 'admin'
            file_obj = request.FILES.get('file_name', None)
            if not file_obj:
                return Response(data={'code': 0, 'desc': '获取不到文件对象'})
            logger.info(f'用户：{username} 本次上传的文件为：{file_obj}')
            file_name = file_obj.name
            if not (file_name.endswith('.xls') or file_name.endswith('.xlsx')):
                return Response(data={'code': 0, 'desc': '请上传后缀为 .xls 或 .xlsx 的 excel 文件!'})
            # 重新拼接文件名, 假设文件名 file_test.xls
            file_info = file_name.split('.')  # ['file_test', 'xls']
            new_file_name = f'{file_info[0]}_{username}.{file_info[1]}'
            # 检查目录是否存在, 不存在则新建
            if not os.path.exists(UPLOAD_ROOT):
                os.makedirs(UPLOAD_ROOT)
            file_path = os.path.join(UPLOAD_ROOT, new_file_name)
            # 假设之前已经上传了一份文件, 但用户没有下载处理结果的 excel 文件, 则给出提示
            ret_file_path = f'{DOWNLOAD_ROOT}测试数据处理结果_{username}.xls'
            if os.path.exists(ret_file_path):
                return Response(data={'code': 0, 'desc': '请先下载之前上传文件后的处理结果!'})
            # 分块写入文件, 使用 chunks() 代替 read() 可以在读取大文件时尽量减少对系统内存的占用
            with open(file_path, 'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)

            # 保存文件后, 将其放到任务队列进行异步处理
            # 注意, 前面已经提到, 这里不使用 .delay() 方法
            task = celery_test.apply_async(args=(file_path, username))
            # 这里把 task.id 传给前端, 目的是
            return Response(data={'code': 1, 'desc': 'excel文件上传成功, 请稍后查看具体进度', 'task': task.id})
        except Exception as e:
            logger.info(f'处理测试文件失败：{e}')
            return Response(data={'code': 0, 'desc': f'处理测试文件失败：{e}'})
```

#### 6. tasks.py 处理 excel 文件内容

```python
# oms_test/celery_tasks/tasks.py
import time
import loguru
from oms_test.celery import app
from celery_once import QueueOnce
from oms_test.settings import FILE_LOG
logger = loguru.logger
logger.add(f'{FILE_LOG}celery_tasks/tasks.log', format='{time} {level} {message}', level='INFO')


@app.task(base=QueueOnce, once={'graceful': True})
def celery_test(file_path, username):
    start_time = time.time()
    fail_list = deal_excel_content(file_path, username)
    # res = record_wrong_application(fail_reason, username)
    end_time = time.time()
    time_count = end_time - start_time
    return time_count


def deal_excel_content(file_path, username):
    """处理 excel 文件内容"""
    fail_list = list()
    return fail_list
```

#### 7. 分配路由

```python
# oms_test/celery_tasks/urls.py
from django.urls import path
from .views import DealExcelInfoView

urlpatterns = [
    path('test_celery/', DealExcelInfoView.as_view()),  # 测试 Celery 处理 excel 接口
]
```

#### 8. Postman 测试

```python
#　GET 请求，输入 URL： http://127.0.0.1:8000/celery_tasks/test_celery/?file_name=测试模板文件.xls&task_id=
# 点击 Send，发现有结果了。回到 Pycharm，我们在下方的 Run 窗口查看相关信息：
Performing system checks...

System check identified no issues (0 silenced).
March 13, 2021 - 03:39:42
Django version 3.1.3, using settings 'oms_test.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
# 注意：这是我们之前使用的中间件的日志信息
2021-03-13 03:43:00.113 | INFO     | utils.custom_middleware:process_request:26 - 请求参数：{'开始时间': 1615606980.1111271, 'query_params': {'file_name': '测试模板文件.xls', 'task_id': ''}}
2021-03-13 03:43:00.180 | INFO     | utils.custom_middleware:process_response:50 - 响应参数：{'结束时间': 1615606980.1803145, 'data': []}
[13/Mar/2021 03:43:00] "GET /celery_tasks/test_celery/?file_name=%E6%B5%8B%E8%AF%95%E6%A8%A1%E6%9D%BF%E6%96%87%E4%BB%B6.xls&task_id= HTTP/1.1" 200 4759

# 假设 URL 传的参数不完整，试试这个：http://127.0.0.1:8000/celery_tasks/test_celery/?file_name=测试模板文件&task_id=
# 点击 Send，查看运行结果：
2021-03-13 03:45:00.235 | INFO     | utils.custom_middleware:process_request:26 - 请求参数：{'开始时间': 1615607100.2348151, 'query_params': {'file_name': '测试模板文件', 'task_id': ''}}
2021-03-13 03:45:00.247 | INFO     | utils.custom_middleware:process_response:50 - 响应参数：{'结束时间': 1615607100.246982, 'data': {'code': 0, 'desc': '模板文件未找到, 或您已下载过处理结果'}}
[13/Mar/2021 03:45:00] "GET /celery_tasks/test_celery/?file_name=%E6%B5%8B%E8%AF%95%E6%A8%A1%E6%9D%BF%E6%96%87%E4%BB%B6&task_id= HTTP/1.1" 202 73


# 使用 POST 请求再试试上传一份文件到项目中
# GET 请求，输入 URL： http://127.0.0.1:8000/celery_tasks/test_celery/
# 选择 Body，选择 form-data，在 KEY 选择 File，输入 file_name (因为后端我们获取的参数是这个)，Value 上传一个 excel 文件，点击 Send
# Postman 运行结果：
{
    "code": 1,
    "desc": "excel文件上传成功, 请稍后查看具体进度",
    "task": "fe4cb144-8312-4f79-aa7f-7f2f315e03bf"
}
# 查看 oms_test/files/upload/，发现有 测试_admin.xls 文件，说明运行成功！
```

#### 9. excel 文件导出数据公用配置

```python
# oms_test/utils/excel_config.py
import io
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


class XlsExporter(object):
    """
    数据导出到 excel, 依赖包 xlwt, 导出文件行数限制65535
    >>> xe = XlsExporter()
    >>> data = [
    ... [1, 'aa', '2020-01-01'],
    ... [2, 'bb', '2020-01-02'],
    ... ]
    >>> xe.add_sheet(data, sheetname='sheet', headers=('col1', 'col2', 'col3'))
    字典数据导出
    >>> from collections import OrderedDict
    >>> data_dict = [
    ... {'a': 1, 'b': '2020-01-01'},
    ... {'a': 2, 'b': '2020-01-02'},
    ... ]
    >>> header_map = OrderedDict([('a', 'col1'), ('b', 'col2')])
    >>> xe.add_sheet_by_dict(data=data_dict, header_map=header_map, sheetname='sheet2')

    >>> xe.to_file('./test.xls')    # 直接保存本地文件
    >>> bio = xe.to_bio()           # 保存到BytesIO对象
    """

    def __init__(self, header_style, value_style):
        self.wb = xlwt.Workbook(encoding='utf-8')
        self.header_style = header_style  # 表头设置
        self.value_style = value_style  # 内容设置

    def add_sheet(self, data, headers=None, sheet_name='sheet', cell_overwrite_ok=False):
        """ 源数据为列表/元组格式 """
        sheet = self.wb.add_sheet(sheetname=sheet_name, cell_overwrite_ok=cell_overwrite_ok)
        first_row = 0
        if headers:
            for c, header in enumerate(headers):
                sheet.write(0, c, header, self.header_style)
                sheet.col(c).width = 256 * 20  # 列的宽度
            first_row = 1

        for r, line in enumerate(data, first_row):
            for c, item in enumerate(line):
                sheet.write(r, c, item, self.value_style)

    def add_sheet_by_dict(self, data, header_mapping, sheet_name='sheet', cell_overwrite_ok=False):
        """ 源数据为字典格式 """
        fields, headers = zip(*header_mapping.items())
        data_list = list()
        for item in data:
            data_list.append([item.get(f, None) for f in fields])
        self.add_sheet(data_list, headers=headers, sheet_name=sheet_name, cell_overwrite_ok=cell_overwrite_ok)

    def to_bio(self):
        bio = io.BytesIO()
        self.wb.save(bio)
        bio.seek(0)
        return bio

    def to_file(self, file_path):
        self.wb.save(file_path)


def export_to_bio(header_style, value_style, data_dict, header_map, sheet_name='sheet'):
    """ 数据 excel 导出到 BytesIO """
    xe = XlsExporter(header_style, value_style)
    xe.add_sheet_by_dict(data_dict, header_map, sheet_name=sheet_name)
    return xe.to_bio()


def export_to_file(header_style, value_style, data_dict, header_map, file_path, sheet_name='sheet1'):
    """数据 excel 导出到文件"""
    xe = XlsExporter(header_style, value_style)
    xe.add_sheet_by_dict(data_dict, header_map, sheet_name=sheet_name)
    xe.to_file(file_path)
    return
```

#### 10. 获取模型类中字段名与 verbose_name 的对应关系

```python
# oms_test/utils/fileds_verbose_name.py
from django.apps import apps


def get_fields_verbose_name(app_name, model_name):
    """
    获取模型类的字段名和 verbose_name 对应的内容
    :param app_name: 子应用名称
    :param model_name: 模型类名称
    :return: {字段名：verbose_name}
    """
    model_obj = apps.get_model(app_name, model_name)
    mapping_dict = dict()
    for field in model_obj._meta.fields:
        mapping_dict[field.name] = field.verbose_name

    return mapping_dict
```

#### 11. 导出数据示例

这里以导出店铺账户信息示例，store 子应用新建 serializers.py 文件

```python
# oms_test/store/serializers.py
from .models import Store
from rest_framework import serializers


class StoreInfoSerializer(serializers.ModelSerializer):
    """权限记录序列化器"""

    class Meta:
        model = Store
        fields = "__all__"
        read_only_fields = ['last_download_time']
```

编写导出数据函数进行测试

```python
# oms_test/store/views/export_store_infos.py
import os
import django
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oms_test.settings')
django.setup()
import xlwt
from datetime import datetime
from store.models import Store
from collections import OrderedDict
from oms_test.settings import DOWNLOAD_ROOT
from store.serializers import StoreInfoSerializer
from utils.fields_verbose_name import get_fields_verbose_name
from utils.excel_config import set_excel_style, export_to_file


def export_test():
    """测试数据导出到 excel 文件功能"""
    try:
        store_infos = Store.objects.all()
        # 假设数据量太大, 可使用切片方式设置每次导出的数据, 比如第一次[:101], 第二次[101:201]...
        # store_infos = store_infos[:10001]
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_name = f"测试数据导出功能_admin_{current_time}.xls"
        # file_path = os.path.join(DOWNLOAD_ROOT, 'test_files/')
        # if not os.path.exists(file_path):
        #     os.makedirs(file_path)
        file_path = os.path.join(DOWNLOAD_ROOT, file_name)
        serializer = StoreInfoSerializer(store_infos, many=True)
        # 设置表头和内容样式
        head_style = set_excel_style(color='light_orange', name=u'微软雅黑', bold=True, height=240)
        value_style = set_excel_style(height=180, horz=xlwt.Alignment.HORZ_LEFT)
        # 表头字段内容
        header_mapping = get_fields_verbose_name('store', 'Store')
        header_mapping = OrderedDict(header_mapping)
        export_to_file(header_style=head_style, value_style=value_style, data_dict=serializer.data,
                       header_map=header_mapping, file_path=file_path, sheet_name='店铺账户信息')
        print('导出数据成功, 请查看 oms_test/files/download/ 路径下是否已经生成对应的文件!')
    except Exception as e:
        print(f'导出数据失败：{e}')


if __name__ == '__main__':
    export_test()
   
# 运行该文件，结果示例，根据提示查看, 该路径下的确有个新文件：测试数据导出功能_admin_2021-03-13 07:22:48.xls
导出数据成功, 请查看 oms_test/files/download/ 路径下是否已经生成对应的文件!
```



