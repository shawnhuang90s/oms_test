[TOC]

### 项目中生成 API 文档

#### 1. 安装 apidoc

>参考资料：https://blog.csdn.net/qq_41601960/article/details/103583676

```bash
npm install apidoc -g
# 升级版本
npm install -g npm
# 运行以下命令
apidoc -i myapp/ -o apidoc/ -t mytemplate/
# 运行结果如下, 提示要创建一个 apidoc.json 之类的文件
{"message":"Please create an apidoc.json or apidoc.config.js configuration file or add an 'apidoc' key to your package.json.","level":"warn"}
{"Path":"/home/yanfa","level":"error","message":"No files found."}
```

#### 2. 项目根目录下新建 apidoc.json 文件

```json
{
  "name": "OMS API DOCUMENTS",
  "version": "1.0.0",
  "description": "订单管理系统前后端联调的接口文档",
  "title": "API接口文档",
  "url" : "https://127.0.0.1:8080",
  "template": {
    "withCompare": true,
    "withGenerator": true,
    "aloneDisplay": false
  }
}
```

#### 3. apidoc 在项目中的配置

```python
# 项目根目录下新建 api_doc 目录

# oms_test/oms_test/settings.py
# 文件开头导入 os 模块
import os
......
INSTALLED_APPS = [
    ......
    # 这里注释掉
    # 'django.contrib.staticfiles',

    # 自建应用
    'store.apps.StoreConfig',
]
......
STATIC_URL = '/static/'
# 添加路径
API_DOC_ROOT = os.path.join(BASE_DIR, 'api_doc/')
```

#### 4. 添加路径

```python
# oms_test/oms_test/settings.py
from django.views.static import serve
from oms_test.settings import API_DOC_ROOT
from django.urls import path, include, re_path

urlpatterns = [
    path('store/', include(('store.urls', 'store'), namespace='store')),
    re_path('api_doc/(?P<path>.*)', serve, {'document_root': API_DOC_ROOT}),
]
```

#### 5. 项目子应用下添加文档文件

```python
# oms_test/store/documents.py
"""
@api {GET} /store/store_account/ 查询Redis中店铺账户信息
@apiVersion 1.0.0
@apiName redis_query
@apiGroup Store
@apiDescription 查询Redis中店铺账户信息

@apiParam {String} key 店铺ID

@apiParamExample {String} 请求参数示例
http://127.0.0.1:8080/store/store_account/?key=54

@apiSuccessExample {Json} 查询成功示例
HTTP 1.1/ 200K
{
    "url": "url_54",
    "app_key": "app_key_54",
    "app_secret": "app_secret_54",
    "access_token": "access_token_54"
}
@apiErrorExample 查询失败示例
HTTP 1.1/ 200K
"Redis中没有店铺ID:aa 对应的账户信息"
"""
```

#### 6. 执行文档生成命令

```bash
# api_doc 目录下新建 docs 目录
# 打开 Pycharm 终端，执行命令
# 命令语法格式：
# apidoc -i 包含注释信息的 .py 文件 -o 自动生成文档的目录
# 这里的 ./ 表示在当前项目根目录下的所有包含注释信息的 .py 文件
# api_doc/ 表示将生成的文件放在 api_doc 目录下
# 如果文档更新了，或者项目中其他地方也有接口文档，再次执行该命令即可
apidoc -i ./ -o api_doc/
```

#### 7. 验证是否生成文档

重启项目，浏览器访问以下 URL 查看效果

>http://127.0.0.1:8080/api_doc/index.html

#### 8. 忽略文件新增忽略内容

>api_doc/ 目录下的内容显然没有必要上传到远程仓库，因此要忽略它

```bash
# oms_test/.gitignore
.idea/
*.pyc
__pycache__/
oms_conf/
*/migrations/*
api_doc/
```

由于 git 已经有本地缓存，因此必须删除缓存，再把代码重新上传到远程仓库，否则忽略文件不生效

```bash
# 打开 Pycharm 终端
git rm -r -f --cached .
git add .
git commit -m '项目中自动生成 API 文档/添加忽略文件并重新上传代码到远程仓库'
git push origin master
```

### 权限验证

现在 Redis 查询接口和文档都有了，接下来该设置权限限制用户的访问

#### 1. 新建 user/system 子应用

```bash
# 打开 Pycharm 终端
python manage.py startapp user
python manage.py startapp system
```

#### 2. 添加到配置文件中

```python
# oms_test/oms_test/settings.py
INSTALLED_APPS = [
	......
    # 自建应用
    'store.apps.StoreConfig',
    'user.apps.UserConfig',
    'system.apps.SystemConfig',
]
```

#### 3. 新建 User 模型类

这里假设不继承 Django 自带的 AbstractUser 模型，自定义一个用户模型类

```python
# oms_test/user/models.py
from django.db import models


class User(models.Model):
    """继承 Django 自带的用户表并新增字段"""
    id = models.AutoField(primary_key=True, verbose_name='用户ID')
    username = models.CharField(max_length=50, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=50, verbose_name='密码')
    is_superuser = models.BooleanField(default=False, verbose_name='是否是超级用户')
    email = models.CharField(max_length=50, blank=True, verbose_name='邮箱')
    is_active = models.BooleanField(default=True, verbose_name='在职/离职状态')
    date_joined = models.DateTimeField(verbose_name='加入时间')

    class Meta:
        managed = False
        db_table = 'oms_user'
        app_label = 'user'
        verbose_name = verbose_name_plural = '用户表'

    def __str__(self):
        # 优先显示用户名, 其次是ID
        return str(self.username) or str(self.id)
```

把建表语句添加进 oms_table.sql 

```mysql
CREATE TABLE `oms_store` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '店铺ID',
  `name` varchar(200) DEFAULT NULL COMMENT '店铺名',
  `manager_name` varchar(100) DEFAULT NULL COMMENT '店铺负责人',
  `manager_id` int(11) DEFAULT NULL COMMENT '店铺负责人ID',
  `center` varchar(100) DEFAULT NULL COMMENT '渠道中心',
  `center_id` int(11) DEFAULT NULL COMMENT '渠道中心ID',
  `platform` varchar(45) DEFAULT NULL COMMENT '平台名',
  `market` varchar(200) DEFAULT NULL COMMENT '站点',
  `market_id` int(11) DEFAULT NULL COMMENT '站点ID',
  `status` tinyint(2) DEFAULT NULL COMMENT '店铺状态',
  `last_download_time` DATETIME DEFAULT NULL COMMENT '上次抓单时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT '店铺表';


CREATE TABLE `oms_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `password` varchar(50) NOT NULL COMMENT '密码',
  `is_superuser` tinyint(1) DEFAULT FALSE COMMENT '是否是超级用户',
  `email` varchar(50) DEFAULT NULL COMMENT '邮箱',
  `is_active` tinyint(1) NOT NULL COMMENT '在职/离职状态',
  `date_joined` datetime(6) NOT NULL COMMENT '新建用户加入时间记录',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT '用户表';
```

Pycharm 打开之前提到的 oms_test@localhost[console] 页面，执行上面的建表语句

#### 4. Redis 查询接口添加权限验证

新建权限验证文件 permissions.py 

```python
# oms_test/utils/permissions
from user.models import User
from rest_framework.permissions import BasePermission

class APIPermission(BasePermission):
    """访问API接口需要权限验证"""
    def has_permission(self, request, view):
        try:
            print(request.user)
            User.objects.get(username=request.user)
        except User.DoesNotExist:
            # 目前表里没添加数据, 默认都可以访问
            return True
        return False
```
配置文件添加限制条件

```python
# oms_test/oms_test/settings.py
......
REST_FRAMEWORK = {
    # 全局设置, 默认所有接口都需要被验证
    'DEFAULT_PERMISSION_CLASSES': (
        'utils.permissions.APIPermission',
    ),
}
```

测试权限验证是否生效：重启项目，Postman 运行 Redis 查询接口：http://127.0.0.1:8080/store/store_account/?key=2，Pycharm 下方的 Run 窗口查询打印信息，说明该接口走了权限验证方法

```python
Performing system checks...

Watching for file changes with StatReloader
System check identified no issues (0 silenced).
December 21, 2020 - 03:54:28
Django version 3.1.3, using settings 'oms_test.settings'
Starting development server at http://127.0.0.1:8080/
Quit the server with CONTROL-C.
AnonymousUser
[21/Dec/2020 03:54:30] "GET /store/store_account/?key=2 HTTP/1.1" 200 49
```





