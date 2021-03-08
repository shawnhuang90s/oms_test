[TOC]

### uWSGI 的使用

> uWSGI 是一个快速的，自我驱动的，对开发者和系统管理员友好的应用容器服务器

#### 1. 安装 uWSGI

```bash
python -m pip install uwsgi
```

#### 2. 新建 uwsgi.ini

```bash
# 首先在 PyCharm 终端查询当前项目的绝对路径
pwd
# 比如我的：/home/yanfa/personal_project/oms_test

# 项目根目录下新建该文件，添加以下内容：
[uwsgi]
# 服务器 IP 及端口
http=0.0.0.0:8000
# 本地项目绝对路径,　如果在服务器或者其他电脑, 记得修改
chdir=/home/yanfa/personal_project/oms_test
# Django 新建项目时自动生成的 wsgi 文件
# 比如本项目在 oms_test/oms_test/wsgi.py
module=oms_test.wsgi:application
# 是否开启主进程管理模式
master=True
# pid 文件路径, 这里就放在项目根目录下
pidfile=uwsgi.pid
# 最大请求数
max-requests=5000
# uwsgi 日志路径, 暂时也放在项目根目录下
daemonize=uwsgi.log
# 进程个数
process=4
# 每个进程的线程个数
threads=2
```

#### 3. 配置文件修改

```python
# oms_test/oms_test/settings.py
DEBUG = False
ALLOWED_HOSTS = ['*']
```

#### 4. 启动 uWSGI，访问

```bash
uwsgi --ini uwsgi.ini
ps -ef | grep uwsgi
# 访问地址： 127.0.0.1:8000/ 看是否有内容
# 如果有的话，表示 uWSGI 配置成功，只要电脑没关机，即服务没有停止运行，就能一直访问
```

#### 5. 编写 sh 文件

```bash
# 项目根目录下新增 Bash Script 格式文件
# oms_test/restart_uwsgi.sh
# 添加以下内容：
#!/usr/bin/env bash
pkill -9 uwsgi
uwsgi --ini uwsgi.ini
ps -ef | grep uwsgi

# PyCharm 终端内测试是否有效
sh restart_uwsgi.sh

# 注意：当电脑或服务器重启时，在重启 uwsgi 之前，先重启 kafka\mysql\redis 等
```

### 邮件发送（编写一个公用类）

```python
# oms_test/utils/send_email.py

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class SendEmail:

    def __init__(self, user=None, password=None, tag=None, content=None, doc=None, cc_list=None, to_list=None):
        """
        :param  user        发送人邮箱账号
        :param  password    发送人邮箱密码
        :param  to_list     收件人邮箱账号列表
        :param  tag         邮箱主题
        :param  content     发送内容
        :param  doc         附件
        """
        self.user = user
        self.password = password
        self.tag = tag
        self.content = content
        self.doc = doc
        self.cc_list = cc_list
        self.to_list = to_list

    def structure_email_content(self):
        """构造邮件内容"""
        attach = MIMEMultipart()
        if self.user is not None:
            # 发件人
            attach['From'] = f'发件人：<{self.user}>'
        if self.tag is not None:
            # 主题
            attach['Subject'] = self.tag
        if self.content:
            email_content = MIMEText(
                self.content.get('content', ''),
                self.content.get('type', 'plain'),
                self.content.get('coding', ''),
            )
            attach.attach(email_content)
        if self.doc:
            # 估计任何文件都可以用 base64, 比如 rar 等
            # 文件名汉字使用 gbk 编码
            name = os.path.basename(self.doc)
            f = open(self.doc, 'rb')
            doc = MIMEText(f.read(), 'base64', 'utf-8')
            doc['Content-Type'] = 'application/octet-stream'
            doc['Content-Disposition'] = 'attachment; filename="' + name + '"'
            attach.attach(doc)
            f.close()
        if self.to_list:
            # 收件人列表
            attach['To'] = ';'.join(self.to_list)
            
        return attach.as_string()

    def send(self):
        """发送邮件"""
        try:
            # 开启邮箱服务
            server = smtplib.SMTP_SSL('smtp.exmail.qq.com', port=465)
            # 登录邮箱
            server.login(self.user, self.password)
            print('邮件开始发送 -------->')
            server.sendmail(f'<{self.user}>', self.to_list, self.structure_email_content())
            server.close()
            print('邮件发送成功 --------<')
        except Exception as e:
            print(f'邮件发送失败：{e}')


if __name__ == '__main__':
    SendEmail(
        user='发送者的邮箱账号',
        password='发送者的邮箱密码',
        tag='这是邮箱主题',
        content={
            'content': '这是测试内容',
            'type': 'plain',
            'coding': 'utf-8'
        },
        to_list=['接收者1的邮箱账号', '接收者2的邮箱账号'],
    ).send()
```

### Django-commands 用法

>基本概念参考：https://www.dazhuanlan.com/2019/10/07/5d9aa090514ba/
>
>简单的说，如果想执行某个 Python 文件，可以按以下示例操作

#### 1. 子应用下新建两个 Python 包

```bash
# 这里我们在 store 子应用下新建这两个包，注意三点：
1.必须是 Python 包，而不是 mkdir 这种新建普通的目录
2.先新建 management 包，再在 management 里面新建 commands 包
3.这两个包必须这样命名，否则后面使用命令执行时找不到对应的内容
# 新建后的目录：oms_test/store/management/commands/
```

#### 2. 安装必要的包

```bash
pip install xlwt
```

#### 3. Django-commands 用法示例

示例1

```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def add_arguments(self, parser):
        """添加参数"""
        parser.add_argument('poll_id', nargs='+', type=str)
        
    def handle(self, *args, **options):
        try:
            arg = options['poll_id'][0]
            if arg == 'test':
                test()
            else: ...
        except Exception as e:
            print(e)

def test():
    pass

# 执行命令格式：python manage.py 当前文件名 test
```

示例2

```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--status', nargs='?', type=str, dest='status', default='default',
            choices=['default', 'isshipped', 'refund'], help='download amazon orders by effective status'
        )

    def handle(self, *args, **kwargs):
        status = kwargs.get('status')
        if status == 'refund':
            sync_refund_order()
        else:...

def sync_refund_order():
    pass

# 执行命令格式：python manage.py 当前文件名 --status refund
```

#### 4. 新增店铺日志配置

```python
# oms_test/oms_conf/oms_log.py
"""日志路径配置"""
import os
import loguru
from pathlib import Path
from datetime import datetime


# 基础路径配置
logger = loguru.logger
current_time = datetime.now().strftime('%Y-%m-%d')
base_dir = Path(__file__).resolve().parent.parent
# 以日期为界限, 每天的日志放一个文件夹内
log_base_path = f'{base_dir}/log/{current_time}/'
if not os.path.exists(log_base_path):
    os.makedirs(log_base_path, exist_ok=False)

# kafka 路径配置
kafka_log = f'{log_base_path}/kafka/'
# store 路径配置
store_log = f'{log_base_path}/store/'
```

#### 5. 编写脚本

```python
# oms_test/store/management/commands/send_store_info.py
import os
import xlwt
import loguru
from django.db import connection
from oms_test.settings import BASE_DIR
from utils.send_email import SendEmail
from oms_test.settings import STORE_LOG
from django.core.management.base import BaseCommand
logger = loguru.logger
logger.add(f'{STORE_LOG}send_store_info.log', format='{time} {level} {message}', level='INFO')


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            send_store_info()
        except Exception as e:
            logger.error(f"发送店铺信息失败：{e}")


def send_store_info():
    """发送店铺信息到相关负责人的邮箱"""
    sql_str = "select name, manager_name, center, platform, market from oms_store where status in (1, 3, 5);"
    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        store_infos = cursor.fetchall()
        logger.info(f"查询出的店铺信息：{store_infos}")
        if store_infos:
            # 新建 excel 文件
            n = 1
            file_obj = xlwt.Workbook(encoding='utf-8')
            sheet_obj = file_obj.add_sheet('data')
            sheet_obj.write(0, 0, "店铺名")
            sheet_obj.write(0, 1, "负责人")
            sheet_obj.write(0, 2, "所属中心")
            sheet_obj.write(0, 3, "所属平台")
            sheet_obj.write(0, 4, "所属市场")
            # 将店铺信息写入 excel 文件
            for obj in store_infos:
                name, manager_name, center, platform, market = obj
                sheet_obj.write(n, 0, str(name))
                sheet_obj.write(n, 1, str(manager_name))
                sheet_obj.write(n, 2, str(center))
                sheet_obj.write(n, 3, str(platform))
                sheet_obj.write(n, 4, str(market))
                logger.info(f"********* 已将第 {n} 条符合条件的订单信息保存进 excel 文件中 **********")
                n += 1

            if n > 1:
                file_path = f"{BASE_DIR}/store_infos.xls"
                file_obj.save(file_path)
                content = f"""Hi, all:
                附件是店铺相关信息
                相关详情烦请查看 excel 文件, 谢谢!"""
                SendEmail(
                    user='输入发送者的邮箱账号',
                    password='输入发送者的邮箱账号密码',
                    to_list=['接收者的邮箱账号(可以是同一个)'],
                    tag=f'店铺信息整理',
                    content={
                        'content': content,
                        'type': 'plain',
                        'coding': 'utf-8'
                    },
                    doc=file_path
                ).send()
                # 发送邮件后将其删除
                os.remove(file_path)


if __name__ == '__main__':
    send_store_info()
```

#### 6. 测试发送邮件是否生效（附件添加 excel 文件）

```python
# PyCharm 终端输入以下命令，执行后发现接受者的邮箱马上就收到了一封邮件
python manage.py send_store_info
```

### 登录验证装饰器

```python
# oms_test/utils/decorator_func.py
from rest_framework import status
from rest_framework.response import Response


def login_auth(func):
    """登录验证装饰器"""
    @wraps(func)
    def inner(request, *args, **kwargs):
        session_id = request.COOKIES.get('sessionid', None)
        messages = request.COOKIES.get('messages', None)
        if session_id and messages:
            return func(request, *args, **kwargs)
        else:
            return Response({'code': 0, 'desc': '请登录后再访问'}, status=status.HTTP_401_UNAUTHORIZED)

    return inner
```

### 验证当前用户是否是超管装饰器

#### 1. 从 COOKIES 中获取用户名 

```python
# oms_test/utils/get_username.py
def get_username(request):
    """从 COOKIES 中获取用户名"""
    try:
        cookie = request.COOKIES
        if "messages" not in cookie.keys():
            return None
        messages = cookie["messages"].split("$")[1]
        try:
            info = messages.split('."]')[0].split(", ")[1]
        except Exception:
            info = messages.split('."]')[0].split("as ")[1]
        username = info.encode("utf-8").decode("unicode_escape")
    except Exception:
        return None

    return username
```

#### 2. 装饰器的实现

```python
# oms_test/decorator_func.py
from functools import wraps
from user.models import User
from rest_framework import status
from utils.get_username import get_username
from rest_framework.response import Response


def login_auth(func):
    """登录验证装饰器"""
    @wraps(func)
    def inner(request, *args, **kwargs):
        session_id = request.COOKIES.get('sessionid', None)
        messages = request.COOKIES.get('messages', None)
        if session_id and messages:
            return func(request, *args, **kwargs)
        else:
            return Response({'code': 0, 'desc': '请登录后再访问'}, status=status.HTTP_401_UNAUTHORIZED)

    return inner


def admin_auth(func):
    """超管校验装饰器"""
    @wraps(func)
    def inner(self, request, *args, **kwargs):
        username = get_username(request)
        if not username:
            return Response({"code": 0, "desc": "获取用户名失败"}, status=status.HTTP_200_OK)
        user_obj = User.objects.filter(username=username).first()
        if not user_obj:
            return Response({"code": 0, "desc": "用户名不存在"}, status=status.HTTP_200_OK)
        if user_obj.is_superuser == True:
            return func(self, request, *args, **kwargs)
        else:
            return Response({"code": 0, "desc": "您没有权限执行此操作!"}, status=status.HTTP_200_OK)

    return inner
```

### 提供选择用户接口

#### 1. 视图处理

```python
# oms_test/user/views.py
from user.models import User
from rest_framework.views import APIView
from utils.decorator_func import login_auth
from rest_framework.response import Response
from django.utils.decorators import method_decorator


class UserListView(APIView):
    """用户信息展示接口"""
	
    # 测试的时候把登录验证装饰器注释掉
    # @method_decorator(login_auth)
    def get(self, request):
        try:
            user_list = [i.username for i in User.objects.all()]
        except Exception as e:
            print(e)
            user_list = []
        ret = {'code': 1, 'data': user_list}

        return Response(data=ret)
```

#### 2. 路径配置

```python
# oms_test/oms_test/urls.py
urlpatterns = [
    ......
    path('store/', include(('store.urls', 'store'), namespace='store')),
    path('user/', include(('user.urls', 'user'), namespace='user')),
    ......
]

# oms_test/user/urls.py
from django.urls import path
from .views import UserListView

urlpatterns = [
    path('user_list/', UserListView.as_view()),  # 选择用户接口
]
```



#### 



