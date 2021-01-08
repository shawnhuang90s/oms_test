[TOC]

## 订单管理系统

### 准备工作

#### 1. 登录云服务器

```bash
# 假设有个自己的云服务器
ssh -l root 182.254.177.42
```

#### 2. 假设系统中的 Python3 版本比较低，想卸载后下载更高版本

```bash
# 卸载 Python3
rpm -qa|grep python3|xargs rpm -ev --allmatches --nodeps
# 删除所有残余文件
whereis python3 |xargs rm -frv
# 查看系统中的 Python 版本
whereis python
```

#### 3. CentOS7 安装 Python3 版本

```bash
# 更新系统软件包
yum update -y

# 安装软件管理包和可能使用的依赖
yum -y groupinstall "Development tools"
yum install openssl-devel bzip2-devel expat-devel gdbm-devel readline-devel sqlite-devel

# 下载 Pyhton3
wget https://www.python.org/ftp/python/3.8.1/Python-3.8.1.tgz

# 解压
tar -zxvf Python-3.8.1.tgz

# 编译安装到指定路径
cd Python-3.8.1
./configure --prefix=/usr/local/python3
make && make install

# 建立软链接，添加变量，方便在终端中直接使用 Python3
ln -s /usr/local/python3/bin/python3.8 /usr/bin/python3

# Python3 安装完成之后 pip3 也一块安装完成，不需要再单独安装，一样建立软链接
# 如果提示已存在 /usr/bin/pip3，就先删除它
rm -rf /usr/bin/pip3
ln -s /usr/local/python3/bin/pip3.8 /usr/bin/pip3

# 更新 pip3
pip3 install --upgrade pip

# 查看是否已经有 Python3 和 pip3
python3
pip3 -V

# 设置 Python 默认版本，当前默认是 Python2
python
Python 2.7.5 (default, Aug  7 2019, 00:51:29) 
[GCC 4.8.5 20150623 (Red Hat 4.8.5-39)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> exit()

# 备份原来的软连接
mv /usr/bin/python /usr/bin/python.bak
# 创建新的软连接
ln -s /usr/local/python3/bin/python3 /usr/bin/python
# 查看 Python 默认版本
python
Python 3.8.1 (default, Dec  7 2020, 11:56:21) 
[GCC 4.8.5 20150623 (Red Hat 4.8.5-44)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> exit()

# 再返回2.7版本
whereis python
rm -f /usr/bin/python
ln -s /usr/bin/python2
ln -s /usr/bin/python2.7 /usr/bin/python
python
```

### 虚拟环境

#### 1. 下载 virtualenv 和 virtualenvwrapper

```bash
pip3 install virtualenv
pip3 install virtualenvwrapper
# 如果报错：
ModuleNotFoundError: No module named '_ctypes'
    ----------------------------------------
ERROR: Command errored out with exit status 1: python setup.py egg_info Check the logs for full command output.
# 版本问题导致，解决：
vim /usr/bin/yum # 将首行的 Python 改为 Python2.7
vim /usr/libexec/urlgrabber-ext-down # 与上面同理
# 安装外部函数库
yum install libffi-devel -y

# 重新安装 Python3
cd Python-3.8.1
./configure --prefix=/usr/local/python3
make && make install
pip3 install virtualenvwrapper

# 配置文件添加虚拟环境路径
find / -type f -name 'virtualenvwrapper.sh' 
# 复制上面的结果，把下面内容添加到 .bashrc 文件末尾
vim ~/.bashrc

# 指定virtualenvwrapper执行的python版本
VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
# 指定虚拟环境存放目录，.virtualenvs目录名可自拟
export WORKON_HOME=$HOME/.virtualenvs
# virtualenvwrapper.sh所在目录
source /usr/local/python3/bin/virtualenvwrapper.sh   

# 保存退出，重新激活该文件
source ~/.bashrc
```

#### 2. 新建虚拟环境

```bash
wrokon
mkvirtualenv oms_test -p python3
# 如果没报错，说明没问题；反之，如果新建时报错：
which: no virtualenv in (/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin)
ERROR: virtualenvwrapper could not find virtualenv in your path
# 解决办法：
find / -type f -name 'virtualenv*'
# 把这个复制
/usr/local/python3/bin/virtualenv

vim ~/.bashrc
# 指定virtualenvwrapper执行的python版本
VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
# 指定虚拟环境存放目录，.virtualenvs目录名可自拟
export WORKON_HOME=$HOME/.virtualenvs
# 添加 virtualenv 的路径
export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/python3/bin/virtualenv
# virtualenvwrapper.sh所在目录
source /usr/local/python3/bin/virtualenvwrapper.sh   

# 保存退出，重新激活
source ~/.bashrc

wrokon
# -p python3 表示指定使用 Python3 版本(本项目使用的是 Python3.8 版本)
# 云服务器和本地都新建好虚拟环境
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

### 添加配置文件夹

1. 项目中的配置文件一般包含跟数据库相关的很多敏感信息，因此最好不要把配置信息同步更新到远程仓库
2. 在项目根目录下新建一个文件夹 oms_conf，专门存放项目的配置文件信息

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

### CentOS7 中安装 MySQL

#### 1. 检测系统中是否有 MySQL

> 参考资料：https://www.runoob.com/mysql/mysql-install.html

```bash
rpm -qa | grep mysql

# 如果有旧版本的，想要卸载的话
# 普通删除模式
rpm -e mysql
# 强力删除模式，如果使用上面命令删除时，提示有依赖的其它文件，则用该命令可以对其进行强力删除
rpm -e --nodeps mysql
```

#### 2.安装资源包

```bash
# 安装 yum 资源包
wget http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm
rpm -ivh mysql-community-release-el7-5.noarch.rpm
yum update
# 安装 MySQL 服务
yum install mysql-server
```

#### 3. 启动 MySQL

```bash
# 设置 MySQL 权限
chown mysql:mysql -R /var/lib/mysql
# 初始化 MySQL
mysqld --initialize
# 启动 MySQL
systemctl start mysqld
# 查看运行状态
systemctl status mysqld
# 验证
mysqladmin --version
# mysqladmin  Ver 8.42 Distrib 5.6.50, for Linux on x86_64
```

#### 4. MySQL 客户端

```bash
# 使用 mysql 命令连接到 MySQL 服务器上，默认情况下 MySQL 服务器的登录密码为空
mysql
show databases;
exit

# 新建用户及密码（示例）
mysqladmin -u root password '123456';
# 以新用户登录 MySQL
mysql -uroot -p
show databases;
exit
```

#### 5. MariaDB 的安装（备选）

> MariaDB 完全兼容 MySQL，包括 API 和命令行，可以说是 MySQL 的代替品

```bash
yum install mariadb-server mariadb
systemctl start mariadb  	# 启动 MariaDB
systemctl stop mariadb  	# 停止 MariaDB
systemctl restart mariadb  	# 重启 MariaDB
systemctl enable mariadb  	# 设置开机启动
```

### MySQL 数据库的配置

#### 1. 本地登录 MySQL 

```bash
mysql -uroot -p
```

#### 2. MySQL 修改密码的方法示例

```mysql
# 假设本地的 MySQL 登录密码与上面配置文件的不一样，登录，再修改
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
from oms_conf import oms_db
DATABASES = oms_db.DATABASES
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
```

#### 6. 安装 pymysql

```bash
pip install -i https://pypi.doubanio.com/simple/ pymysql
```

#### 7. 导入 pymysql 包

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

### 添加忽略文件 .gitignore

项目中有些文件是不需要上传到远程仓库的，因此要配置一下. 项目根目录下新建 .gitignore 文件

```bash
# oms_test/.gitignore
.idea/
*.pyc
__pycache__/
oms_conf/
```

由于 git 已经有本地缓存，因此必须删除缓存，再把代码重新上传到远程仓库，否则忽略文件不生效

```bash
# 打开 Pycharm 终端
git rm -r -f --cached .
git add .
git commit -m '添加忽略文件并重新上传代码到远程仓库'
git push origin master
```

### 第一次运行项目

```bash
打开 manage.py 文件 -> 右键点击 Run 'manage'
# 如果报错提示如下，表示 MySQL 版本冲突
File "/home/yanfa/.virtualenvs/oms_test/lib/python3.7/site-packages/django/db/backends/mysql/base.py", line 36, in <module>
    raise ImproperlyConfigured('mysqlclient 1.4.0 or newer is required; you have %s.' % Database.__version__)
django.core.exceptions.ImproperlyConfigured: mysqlclient 1.4.0 or newer is required; you have 0.10.1.
# 解决办法：点击 raise 上面提示的文件路径, 把跳转到的文件的下面内容注释掉
# if version < (1, 4, 0):
#     raise ImproperlyConfigured('mysqlclient 1.4.0 or newer is required; you have %s.' % Database.__version__)

# 再次运行 manage.py 文件, 如果没有报错
点击左上角 manage.py 框里的三角形 -> 点击 Edit Configurations -> 找到 Parameters，对应框里输入：runserver 127.0.0.1:8080 -> Apply -> OK -> 点击刚才 manage.py 框右边的绿色三角形直接运行项目 -> 此时 Pycharm 下面的 Run 窗口会自动弹开 -> 点击网址：http://127.0.0.1:8080/ -> 自动在浏览器弹出一个网址, 即 Django 运行页面
```
