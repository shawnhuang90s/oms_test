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

### 超管验证装饰器

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

### 权限配置与权限管理

#### 1. 新建子应用 basic

```bash
python manage.py startapp basic

# oms_test/oms_test/settings.py
INSTALLED_APPS = [
    ......
    # 自建应用
    'store.apps.StoreConfig',
    'user.apps.UserConfig',
    'basic.apps.BasicConfig',
]
```

#### 2. 新建公共模型类

```python
# oms_test/utils/base_model.py
import os
import django
from django.db import models
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oms_test.settings')
django.setup()


class BaseModel(models.Model):
    """公共模型类"""

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        # 定义为抽象基类, 表示迁移数据库的时候忽略这个公共模型类
        # 换句话说, 数据库不会创建这个模型类对应的表
        abstract = True
```

#### 3. 查看/操作权限表与记录表的创建

```python
from django.db import models
from user.models import User
from utils.base_model import BaseModel


class PermissionList(BaseModel):
    """权限接口详情表"""

    id = models.AutoField(primary_key=True)
    api_url_address = models.CharField(max_length=256, verbose_name="接口地址")
    request_method = models.CharField(max_length=10, verbose_name="请求方式")
    permission_name = models.CharField(max_length=128, verbose_name="权限名称")

    class Meta:
        managed = False
        db_table = 'oms_permission_list'
        app_label = 'basic'
        verbose_name = verbose_name_plural = '权限接口详情表'
        unique_together = ["api_url_address", "request_method"]
        

class Permission(BaseModel):
    """查看/操作权限表"""

    PERMISSION_TYPE = (
        (0, "查看"),
        (1, "操作"),
    )
    STATE_TYPE = (
        (0, "禁用"),
        (1, "启用"),
    )
    CATEGORY_TYPE = (
        (0, '模块1'),
        (1, '模块2'),
        (2, '模块3'),
    )
    id = models.AutoField(primary_key=True)
    api_name = models.CharField(max_length=64, null=True, blank=True, verbose_name="界面模块")
    permission_list = models.CharField(max_length=64, null=True, blank=True, verbose_name="权限ID组合")
    # 注意：之前有提供用户名接口, 没有传用户ID给前端, 因此这里保存时也只能存用户名. 当然, 也可以在那个接口把 ID 和用户名都传给前端, 这样的话这里保存前端返回的 ID 即可
    executor = models.CharField(max_length=64, verbose_name="执行人")
    operator = models.CharField(max_length=64, verbose_name="操作人")
    permission_type = models.SmallIntegerField(choices=PERMISSION_TYPE, default=0, verbose_name="权限类型")
    is_active = models.SmallIntegerField(choices=STATE_TYPE, default=0, verbose_name="是否启用(默认启用)")
    category = models.SmallIntegerField(choices=CATEGORY_TYPE, default=0, verbose_name='模块类别')

    class Meta:
        managed = False
        db_table = 'oms_permission'
        app_label = 'basic'
        verbose_name = verbose_name_plural = '查看/操作权限表'


class PermissionRecord(BaseModel):
    """查看/操作权限分配记录表"""

    STATE_TYPE = (
        (0, "禁用"),
        (1, "启用"),
    )
    id = models.AutoField(primary_key=True)
    permission = models.ForeignKey(Permission, related_name="permission_id", verbose_name="权限ID", on_delete=models.CASCADE)
    before_change = models.SmallIntegerField(choices=STATE_CHOICES, verbose_name="被修改之前的状态")
    after_change = models.SmallIntegerField(choices=STATE_CHOICES, verbose_name="被修改之后的状态")

    class Meta:
        managed = False
        db_table = 'oms_permission_record'
        app_label = 'basic'
        verbose_name = verbose_name_plural = '查看/操作权限记录表'
```

#### 4. oms_table.sql 表维护并在数据库创建新表

```mysql
# oms_test/doc/oms_table.sql
......
# UNIQUE (`api_url_address`, `request_method`) 设置联合索引
CREATE TABLE `oms_permission_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '权限接口详情ID',
  `api_url_address` varchar(256) DEFAULT NULL COMMENT '接口地址',
  `request_method` varchar(10) DEFAULT NULL COMMENT '请求方式',
  `permission_name` varchar(128) DEFAULT NULL COMMENT '权限名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE (`api_url_address`, `request_method`) 
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT '权限接口详情表';


CREATE TABLE `oms_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '查看/操作权限ID',
  `api_name` varchar(64) DEFAULT NULL COMMENT '界面模块',
  `permission_list` varchar(64) DEFAULT NULL COMMENT '权限ID组合',
  `executor` varchar(64) DEFAULT NULL COMMENT '执行人',
  `operator` varchar(64) DEFAULT NULL COMMENT '操作人',
  `permission_type` tinyint(2) DEFAULT 0 COMMENT '权限类型',
  `is_active` tinyint(2) DEFAULT 0 COMMENT '是否启用(默认启用)',
  `category` tinyint(2) DEFAULT 0 COMMENT '模块类别',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT '查看/操作权限表';


CREATE TABLE `oms_permission_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '查看/操作权限记录ID',
  `before_change` tinyint(2) DEFAULT NULL COMMENT '被修改之前的状态',
  `after_change` tinyint(2) DEFAULT NULL COMMENT '被修改之后的状态',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id`) REFERENCES oms_permission(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT '查看/操作权限记录表';

# Pycharm 点击 Database，按照之前的方法执行上面的 SQL 语句即可
```

#### 5. 添加测试数据示例

```mysql
========== oms_permission_list ==========
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/createapplication/stock_application/','POST','FBA备货申请页面数据查询与展示','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/createapplication/stockapplication/creation/','GET','FBA批量备货模板下载/FBA批量备货处理结果','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/createapplication/stockapplication/creation/','POST','FBA单个备货/FBA导入批量备货','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/createapplication/stockapplication/search/','POST','FBA备货审核和进度页面数据查询与展示','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/createapplication/stockwarehouse/','GET','FBA备货审核和进度页面备货仓下拉展示','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/createapplication/applicationreviewstates/','GET','FBA备货审核和进度页面计划用时/实际用时数据展示','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/createapplication/stockapplications/review/','POST','FBA备货审核和进度页面单个/批量备货单审核/驳回','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/createapplication/stockapplications/revocation/','PUT','FBA备货审核和进度页面单个备货单撤销','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/createapplication/stockapplications/review/excel/','GET','FBA批量审核模板下载/FBA批量审核处理结果','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/createapplication/stockapplications/review/excel/','POST','FBA导入批量审核','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/createapplication/excel/stockapplications/','POST','FBA备货审核和进度页面数据导出','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/createapplication/timeliness_statistics/','GET','FBA备货时效统计表页面','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/basicconfiguration/budgetallocations/','GET','FBA仓备货预算分配页面数据查询与展示','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/basicconfiguration/budgetallocations/next/','GET','FBA仓备货预算分配页面下一级预算分配数据展示','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/basicconfiguration/budgetallocations/','POST','FBA仓备货预算分配页面编辑预算金额','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/basicconfiguration/reviewprocesslist/','GET','FBA审核流程配置页面数据展示','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/basicconfiguration/reviewprocesslist/search/','GET','FBA审核流程配置页面数据查询','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/basicconfiguration/reviewprocesslist/','PUT','FBA审核流程配置页面启用/禁用审核流程','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/basicconfiguration/departments/','GET','FBA创建审核流程时获取指定部门及组(到组一级别)/FBA仓预算配置指定预算分配部门','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/basicconfiguration/positionslevels/','GET','FBA创建审核流程时选择审核流程字段','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/basicconfiguration/reviewprocess/','POST','FBA创建审核流程(确定按钮)','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/basicconfiguration/usernames/','GET','FBA仓预算配置页面选择用户','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/basicconfiguration/departmentprincipals/','POST','FBA仓预算权限配置页面负责人预算权限分配(提交按钮)','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/basicconfiguration/departmentprincipals/','GET','FBA仓预算权限管理页面数据查询与展示','2021-02-01 18:31:52','2021-02-01 18:31:52');
insert into oms_permission_list (api_url_address,request_method,permission_name,create_time,update_time) values ('/api/v1/basicconfiguration/departmentprincipals/','PUT','FBA仓预算权限管理页面删除操作','2021-02-01 18:31:52','2021-02-01 18:31:52');

========= oms_permission ==========
insert into oms_permission (create_time, update_time, api_name, permission_list, executor, operator, permission_type, is_active, category) values ('2021-01-27 06:06:04', '2021-01-27 06:06:04', 'FBA备货申请页面数据查询与展示', '1+2+3+4+5+6+7+8+9+10+11+30', 'root', 'root', 0, 0, 0);
insert into oms_permission (create_time, update_time, api_name, permission_list, executor, operator, permission_type, is_active, category) values ('2021-01-27 06:06:04', '2021-01-27 06:06:04', 'FBA批量备货模板下载/FBA批量备货处理结果', '1+2+3+4+5+6+7+8+9+10+11', 'root', 'root', 0, 0, 0);
insert into oms_permission (create_time, update_time, api_name, permission_list, executor, operator, permission_type, is_active, category) values ('2021-01-27 06:06:04', '2021-01-27 06:06:04', 'FBA单个备货/FBA导入批量备货', '1+2+3+4+5+6+7+8+9+10+11+29', 'root', 'root', 0, 0, 0);
insert into oms_permission (create_time, update_time, api_name, permission_list, executor, operator, permission_type, is_active, category) values ('2021-01-27 06:06:04', '2021-01-27 06:06:04', 'FBA备货审核和进度页面数据查询与展示', '12+13+14+15', 'root', 'root', 0, 0, 0);
insert into oms_permission (create_time, update_time, api_name, permission_list, executor, operator, permission_type, is_active, category) values ('2021-01-27 06:06:04', '2021-01-27 06:06:04', 'FBA备货审核和进度页面备货仓下拉展示', '16+17+18+19+20+21+22+23+24+25', 'root', 'root', 0, 0, 0);
insert into oms_permission (create_time, update_time, api_name, permission_list, executor, operator, permission_type, is_active, category) values ('2021-01-27 06:06:04', '2021-01-27 06:06:04', 'FBA备货审核和进度页面计划用时/实际用时数据展示', '26+27+28', 'root', 'root', 0, 0, 0);
insert into oms_permission (create_time, update_time, api_name, permission_list, executor, operator, permission_type, is_active, category) values ('2021-01-27 06:06:04', '2021-01-27 06:06:04', 'FBA备货审核和进度页面单个/批量备货单审核/驳回', '31+32+33+34+35+36', 'root', 'root', 0, 0, 0);
insert into oms_permission (create_time, update_time, api_name, permission_list, executor, operator, permission_type, is_active, category) values ('2021-01-27 06:06:04', '2021-01-27 06:06:04', 'FBA备货审核和进度页面单个备货单撤销', '37+38+39+40+41+42+43+44+45+46+47+48', 'root', 'root', 0, 0, 0);
insert into oms_permission (create_time, update_time, api_name, permission_list, executor, operator, permission_type, is_active, category) values ('2021-01-27 06:06:04', '2021-01-27 06:06:04', 'FBA批量审核模板下载/FBA批量审核处理结果', '37+38+39+40+41+42+43+44+45+46+47+48', 'root', 'root', 0, 0, 0);
insert into oms_permission (create_time, update_time, api_name, permission_list, executor, operator, permission_type, is_active, category) values ('2021-01-27 06:06:04', '2021-01-27 06:06:04', 'FBA导入批量审核', '37+38+39+40+41+42+43+44+45+46+47+48', 'root', 'root', 0, 0, 0);
```

#### 6. 新增序列化器

```python
# oms_test/basic/serializers.py
from rest_framework import serializers
from .models import PermissionRecord, Permission


class PermissionRecordSerializer(serializers.ModelSerializer):
    """权限记录序列化器"""

    class Meta:
        model = PermissionRecord
        fields = "__all__"
        read_only_fields = ['create_time', 'update_time']


class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化器"""

    class Meta:
        model = Permission
        fields = "__all__"
        read_only_fields = ['create_time', 'update_time']
```

#### 7. 获取权限组合视图

```python
# oms_test/utils/permission_combination.py
def get_permission_combination(api_name, permission_type):
    """获取权限组合ID示例"""
    # 查看权限配置
    if permission_type == 0:
        if api_name == "海外仓备货申请页":
            permission_list = '1'
        elif api_name == "海外仓备货进度查看":
            permission_list = '4+5'
        elif api_name == "海外仓备货审核":
            permission_list = '8'
        elif api_name == "海外仓备货公式配置":
            permission_list = '13+15'
        elif api_name == "海外仓备货系数设置":
            permission_list = '19+22+25'
        elif api_name == "海外仓备货预算分配":
            permission_list = '27+28'
        elif api_name == "待分配调拨清单":
            permission_list = '32'
        elif api_name == "待创建调拨清单":
            permission_list = '45'
        elif api_name == "已创建调拨清单":
            permission_list = '43'
        elif api_name == "备货已结案清单":
            permission_list = '41'
        elif api_name == 'FBA仓备货申请页':
            permission_list = '49'
        elif api_name == 'FBA仓备审核和进度':
            permission_list = '52+54'
        elif api_name == 'FBA仓备货时效统计表':
            permission_list = '60'
        elif api_name == 'FBA仓备货预算分配':
            permission_list = '61+62'
        elif api_name == 'FBA审核流程配置':
            permission_list = '64+65'
        elif api_name == 'FBA仓预算权限配置':
            permission_list = '72'
        else:
            permission_list = ''
    # 操作权限配置(包含查看权限)
    else:
        if api_name == "海外仓备货申请页":
            permission_list = '1+2+3+4'
        elif api_name == "海外仓备货进度查看":
            permission_list = '4+5+6+7'
        elif api_name == "海外仓备货审核":
            permission_list = '8+9+10+11+29'
        elif api_name == "海外仓备货公式配置":
            permission_list = '12+13+14+15'
        elif api_name == "海外仓备货系数设置":
            permission_list = '16+17+19+20+21+22'
        elif api_name == "海外仓备货预算分配":
            permission_list = '26+27+28'
        elif api_name == "待分配调拨清单":
            permission_list = '31+32+33+34+35+36'
        elif api_name == "待创建调拨清单":
            permission_list = '45+46+47+48'
        elif api_name == "已创建调拨清单":
            permission_list = '43+44'
        elif api_name == "备货已结案清单":
            permission_list = '41+42'
        elif api_name == 'FBA仓备货申请页':
            permission_list = '49+50+51'
        elif api_name == 'FBA仓备审核和进度':
            permission_list = '52+54+55+56+57+58+59'
        elif api_name == 'FBA仓备货时效统计表':
            permission_list = '60'
        elif api_name == 'FBA仓备货预算分配':
            permission_list = '61+62+63'
        elif api_name == 'FBA审核流程配置':
            permission_list = '64+65+66+67+68+69'
        elif api_name == 'FBA仓预算权限配置':
            permission_list = '71+72+73'
        else:
            permission_list = ''

    return permission_list
```

#### 8. 分页视图处理

```python
# oms_test/utils/page_settings.py
from rest_framework.pagination import PageNumberPagination


class MyPageNumber(PageNumberPagination):

    page_size = 10  # 每页显示多少条
    page_size_query_param = 'limit'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = 1000  # 每页最大条数数限制
```

#### 9. 权限配置视图处理

```python
# oms_test/basic/views/permission_config.py
from datetime import datetime
from django.db import transaction
from rest_framework.views import APIView
from utils.get_username import get_username
from rest_framework.response import Response
from utils.page_settings import MyPageNumber
from django.utils.decorators import method_decorator
from basic.models import Permission, PermissionRecord
from utils.decorator_func import login_auth, admin_auth
from utils.permission_combination import get_permission_combination
from basic.serializers import PermissionRecordSerializer, PermissionSerializer


class PermissionConfigView(APIView):
    """权限配置"""

    @method_decorator(login_auth)
    @method_decorator(admin_auth)
    def post(self, request):
        """新增权限配置"""

        operator = get_username(request)
        category = request.data.get('category', '')
        executor = request.data.get('executor', None)
        api_name_list = request.data.get('api_name_list', [])
        permission_type = request.data.get('permission_type', None)
        update_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if not api_name_list:
            return Response({"code": 0, "desc": "界面模块名未知"})
        if not permission_type:
            return Response({"code": 0, "desc": "操作权限未知"})
        with transaction.atomic():
            save_point = transaction.savepoint()
            try:
                for api_name in api_name_list:
                    permission_obj = Permission.objects.filter(api_name=api_name, operator=operator,
                                                               permission_type=permission_type).first()
                    # 如果已经创建了权限配置记录, 则更新权限记录表
                    if permission_obj:
                        if permission_obj.is_active == 1:
                            continue
                        permission_obj.is_active = 1
                        permission_obj.update_time = update_time
                        permission_obj.save(update_fields=['is_active', 'update_time'])

                        record_dict = {"permission": permission_obj.id, "before_change": 1, "after_change": 2,
                                       "create_time": update_time, "update_time": update_time}
                        record_serializer = PermissionRecordSerializer(data=record_dict)
                        record_serializer.is_valid(raise_exception=True)
                        record_serializer.save()
                        continue

                    # 没有就新建, 另外记录表也新增数据
                    permission_list = get_permission_combination(api_name, permission_type)
                    data_dict = dict(
                        api_name=api_name,
                        permission_list=permission_list,
                        executor=executor,
                        operator=operator,
                        permission_type=permission_type,
                        is_active=0,
                        category=category,
                        create_time=update_time,
                        update_time=update_time
                    )
                    permission_serializer = PermissionSerializer(data=data_dict)
                    permission_serializer.is_valid(raise_exception=True)
                    new_obj = permission_serializer.save()

                    record_dict = {"permission": new_obj.id, "before_change": 0, "after_change": 1,
                                   "create_time": update_time, "update_time": update_time}
                    record_serializer = PermissionRecordSerializer(data=record_dict)
                    record_serializer.is_valid(raise_exception=True)
                    record_serializer.save()

                return Response({"code": 1, "desc": f"权限分配成功"})
            except Exception as e:
                transaction.savepoint_rollback(save_point)
                return Response({"code": 0, "desc": f"权限分配失败：{e}"})

    @method_decorator(login_auth)
    @method_decorator(admin_auth)
    def get(self, request):
        """查询权限分配信息"""
        executor = request.query_params.get("executor", None)
        is_active = request.query_params.get("is_active", '未知')
        category = request.query_params.get('category', None)
        # 因为数据新建时默认是禁用的, 这里展示的时候也要优先展示禁用的并且按创建时间倒序排列
        permission_infos = Permission.objects.filter(category=category).order_by('-is_active', '-create_time')
        if executor:
            permission_infos = permission_infos.filter(executor=executor)
        if is_active != '未知':
            permission_infos = permission_infos.filter(is_active=is_active)
        count = permission_infos.count()
        page = MyPageNumber()
        page_info = page.paginate_queryset(queryset=permission_infos, request=request, view=self)
        serializer = PermissionSerializer(page_info, many=True)

        return Response({"code": 1, "desc": "succeed", "data": serializer.data, "count": count})


class PermissionRecordListView(APIView):
    """查看权限分配记录"""

    @method_decorator(login_auth)
    @method_decorator(admin_auth)
    def get(self, request):

        category = request.query_params.get('category', None)
        record_infos = PermissionRecord.objects.filter(category=category).order_by('-id')
        count = record_infos.count()
        page = MyPageNumber()
        page_info = page.paginate_queryset(queryset=record_infos, request=request, view=self)
        serializer = PermissionRecordSerializer(page_info, many=True)
        return Response({"code": 1, "desc": "succeed", "data": serializer.data, "count": count})


class PermissionChangeView(APIView):
    """修改权限状态"""

    @method_decorator(login_auth)
    @method_decorator(admin_auth)
    def put(self, request):
        update_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with transaction.atomic():
            save_point = transaction.savepoint()
            try:
                operator = get_username(request)
                pk = request.data.get("id", None)
                is_active = request.data.get("is_active", "未知")
                # 更新权限配置表对应数据的状态
                permission_obj = Permission.objects.get(id=pk)
                before_change = permission_obj.is_active
                permission_obj.is_active = is_active
                permission_obj.operator = operator
                permission_obj.update_time = update_time
                permission_obj.save(update_fields=['is_active', 'operator', 'update_time'])
                # 更新权限记录表对应的状态
                record = {"permission": pk, "before_change": before_change, "after_change": is_active,
                          "create_time": update_time, "update_time": update_time}
                record_serializer = PermissionRecordSerializer(data=record)
                record_serializer.is_valid(raise_exception=True)
                record_serializer.save()
                return Response({"code": 1, "desc": "权限状态修改成功"})
            except Exception as e:
                transaction.savepoint_rollback(save_point)
                return Response({"code": 0, "desc": f"权限状态修改失败：{e}"})
```

#### 10. 路径配置

```python
# oms_test/basic/urls.py
from django.urls import path
from basic.views.permission_config import PermissionConfigView


urlpatterns = [
    path('permission_config/', PermissionConfigView.as_view()),  # 权限配置接口
]
```

#### 11. 权限验证装饰器

```python
# oms_test/utils/decorator_func.py
from functools import wraps
from user.models import User
from rest_framework import status
from utils.get_username import get_username
from rest_framework.response import Response
from basic.models import PermissionList, Permission


......


def permission_auth(func):
    """权限验证装饰器"""
    @wraps(func)
    def inner(request, *args, **kwargs):
        api_url_address = request.path_info
        request_method = request.method
        username = get_username(request)
        permission_obj = PermissionList.objects.filter(api_url_address=api_url_address, request_method=request_method).first()
        if not permission_obj:
            return Response({"code": 0, "desc": "权限详情表中未找到对应的接口"}, status=status.HTTP_200_OK)

        permission_id = permission_obj.id
        permission_infos = Permission.objects.filter(user=username, is_active=1)
        if not permission_infos:
            return Response({"code": 0, "desc": "对不起, 您没有权限!"}, status=status.HTTP_200_OK)
        permission_list = list()
        for obj in permission_infos:
            permission_list_str = obj.permission_list
            id_list = permission_list_str.split('+')
            permission_list.extend(id_list)
        if str(permission_id) in permission_list:
            return func(request, *args, **kwargs)
        else:
            return Response({"code": 0, "desc": "对不起, 您没有权限!"}, status=status.HTTP_200_OK)

    return inner
```







