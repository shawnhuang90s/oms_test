[TOC]

## 订单管理系统

### 新建虚拟环境

```bash
# -p python3 表示指定使用 Python3 版本(本项目使用的是 Python3.7 版本)
mkvirtualenv oms_test -p python3
```

### 新建项目

```bash
# 先安装 Django
# 上面新建虚拟环境后会自动跳转到该虚拟环境
pip install -i https://pypi.doubanio.com/simple/ django
# 切换到想要保存项目的路径，创建项目
cd personal_project/
django-admin startproject oms_test
```

### Pycharm 中添加虚拟环境

```bash
# 上面新建的虚拟环境一般在家目录下的 .virtualenvs 文件夹中
File -> Settings -> 右上角齿轮键 -> Add... -> Existing environment -> ... -> 找到家目录下的 .virtualenvs 文件夹 -> 找到新建的虚拟环境文件夹 oms_test -> bin -> python3.7 -> OK -> Apply -> OK -> 点击 Pycharm 的 Terminal, 查看是否在新建的虚拟环境中 -> (oms_test) yanfa@yanfa-H110SD3-C:~/personal_project/oms_test$
```

### 提交代码到远程仓库

#### 1. GitHub 注册账号, 登录

#### 2. 新建一个仓库：oms_test

#### 3. 提交新建的项目代码到该远程代码仓库

```bash
# 打开 Pycharm 终端
# 本地初始化一个空的 Git 仓库，此时项目根目录下自动生成一个 .git 文件夹
git init 
# 将项目中所有的文件添加进该仓库
git add .
# 将上面添加的内容提交到缓存区, 并添加注释
git commit -m '初始化项目'
# 将本地仓库内的项目同步更新到远程仓库
# 注意, 在远程仓库创建成功时会自动跳转到一个页面
# 有详细的命令告诉我们该怎么提交代码, 包括这里的提交地址
git remote add origin https://github.com/shawnhuang90s/oms.git
# 将本地代码提交到远程仓库的 master 分支(新建仓库默认也只有这个分支)
git push origin mater
```

### 添加配置文件

项目中的配置文件一般包含跟数据库相关的很多敏感信息，因此最好不要把配置信息同步更新到远程仓库
在项目根目录下新建一个文件夹 oms_conf，专门存放项目的配置文件信息

```bash
# 打开 Pycharm 终端
# 新建配置文件夹
mkdir oms_conf
# 切换到该文件夹下，新建数据库配置文件 oms_db.py
cd oms_conf/
vim oms_db.py

# 添加以下内容, 保存并退出
#!/usr/bin/env python
# encoding: utf-8

# 数据库配置
DATABASE = {
    # 默认使用的数据库
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'NAME': 'oms_test',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
    # 只读权限的数据库，这里暂时设置成一样的
    'read_default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'root',
        'USER': 'oms_test',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
}
```

### MySQL 数据库的配置

#### 1. 本地登录 MySQL 

```bash
mysql -uroot -p
```

#### 2. MySQL 修改密码的方法示例

```mysql
# 假设本地的 MySQL 登录密码与上面配置文件的不一样，要修改过来
set password for root@localhost=password('123456');
# 修改成功后退出重新登录
mysql -uroot -p
```

#### 3. 新建数据库

```mysql
# 查看已有的数据库
show databases;
# 新建一个数据库
create database oms_test default charset=utf8;
# 查看是否有该数据库
show databases;
```

#### 4. 导入配置文件内容

```python
# oms_test/oms_test/settings.py
......
from pathlib import Path
......
BASE_DIR = Path(__file__).resolve().parent.parent
from oms_conf import oms_db
```

#### 5. 注释掉配置文件中数据库的配置代码

```python
# oms_test/oms_test/settings.py
......
# 找到 DATABASES 变量对应的字典内容，将其注释掉, 并导入对应的配置信息
DATABASES = oms_db.DATABASE
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
```

#### 6. 安装 Pymysql

```bash
pip install -i https://pypi.doubanio.com/simple/ pymysql
```

#### 7. 导入 Pymysql 包

```python
# oms_test/oms_test/__init__.py
import pymysql
pymysql.install_as_MySQLdb()
```

#### 8. Pycharm 中链接 MySQL

```bash
右上角 Database -> + -> Data Source -> MySQL -> Host: localhost -> Database: oms_test -> User: root -> Password: 123456 -> Test Connection(显示成功) -> Apply -> OK
# 此时发现 Databae 小页面里已经有 oms_test@localhost 的链接了，因为现在还没有迁移数据库, 所以 schemas 的 oms_test 数据库里还没有任何表信息
```

#### 9. 将代码更新到远程仓库

```bash
# 打开 Pycharm 终端
# 查看目前在哪个分支下, 哪些文件做了改动
git status
# 将想要上传的文件添加
git add oms_test/__init__.py oms_test/settings.py
# 放进缓存区并添加注释
git commit -m '数据库的配置'
# 更新到远程仓库
git push origin master
```







