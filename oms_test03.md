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
git rm -rf --cached .
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

测试权限验证是否生效：重启项目，Postman 运行 Redis 查询接口：http://127.0.0.1:8080/store/store_account/?key=2，Pycharm 下方的 Run 窗口查询打印信息（AnonymousUser），说明该接口走了权限验证方法

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

### 日志模块 loguru 基本用法

#### 1. 安装 loguru

```bash
pip install loguru
```

#### 2. 基本用法示例

```python
# oms_test/log_test.py
import sys
from loguru import logger

# debug 测试
logger.debug('this is a test...')
# 2020-12-24 16:53:39.660 | DEBUG    | __main__:<module>:4 - this is a test...

# 注册接收器
logger.add(sys.stderr, format='{time} {level} {message}', filter='my_module', level='INFO')

# 将日志信息输出到文件中（如果没有该文件则自动创建）
logger.add('test_file.log')

# 以当前运行时间节点为依据新建日志文件（每次运行都会新建一个日志文件）
logger.add('test_{time}.log')

# 将日志信息输出到文件中, 并限制每个文件的存储容量
# 这里使用 1KB 来测试（注意：使用大写形式）, 运行后发现自动生成了两个文件
logger.add('test01.log', rotation='1 KB')
for i in range(20):
    logger.info('this is a test...')

# 以某个时间点为依据, 如果时间到了 17:39, 则 test02.log 自动改名（加个当前运行时间后缀）
# 然后又有一个 test02.log 记录 17:39 之后的日志信息, 依次类推
logger.add('test02.log', rotation='17:39')
for i in range(20):
    logger.info('this is a test...')

# 同理, 也可以设置某个时间段来切分该日志文件
logger.add('test02.log', rotation='1 week')

# 每隔固定时间清除日志文件内容
logger.add('test03.log', retention='2 days')

# 将生成的日志文件自动压缩成 .zip 文件
logger.add("test04.log", compression="zip")

# 使用 logger.catch 捕捉程序运行时的任何异常
@logger.catch
def my_function(x, y, z):
    return 1 / (x + y + z)
my_function(0, 0, 0)
# 运行结果：
# 2020-12-24 18:42:20.359 | ERROR    | __main__:<module>:44 - An error has been caught in function '<module>', process 'MainProcess' (8644), thread 'MainThread' (140475222820608):
# Traceback (most recent call last):
#
# > File "/home/yanfa/personal_project/oms_test/log_test.py", line 44, in <module>
#     my_function(0, 0, 0)
#     └ <function my_function at 0x7fc2efa81dd0>
#
#   File "/home/yanfa/personal_project/oms_test/log_test.py", line 42, in my_function
#     return 1 / (x + y + z)
#                 │   │   └ 0
#                 │   └ 0
#                 └ 0
#
# ZeroDivisionError: division by zero

# 默认情况下, 添加到记录器的所有接收器都是线程安全的
# 它们不是多进程安全的, 但是可以将消息排队以确保日志的完整性
# 如果需要异步日志记录, 也可以使用相同的参数
logger.add('test05.log', enqueue=True)
```

Loguru 通过允许显示整个堆栈跟踪信息（包括变量值）来找到问题

```python
# oms_test/log_test.py
from loguru import logger

logger.add('test.log', backtrace=True, diagnose=True)

def func(a, b):
    try:
        a / b
    except Exception:
        logger.exception('运行错误')

func(5, 0)
# 运行结果：
2020-12-25 10:14:00.176 | ERROR    | __main__:func:11 - 运行错误
Traceback (most recent call last):

  File "/home/yanfa/personal_project/oms_test/log_test.py", line 13, in <module>
    func(5, 0)
    └ <function func at 0x7f40ba78ddd0>

> File "/home/yanfa/personal_project/oms_test/log_test.py", line 9, in func
    a / b
    │   └ 0
    └ 5

ZeroDivisionError: division by zero
```

format 属性的设置

```python
# oms_test/log_test.py
from loguru import logger

logger.add("test.log", format="{extra[ip]} {extra[user]} {message}")
context_logger = logger.bind(ip="127.0.0.1", user="Alex")
context_logger.info("上面 bind() 里设置的用户将对应这条信息")
context_logger.bind(user="John").info("可以将参数设置成其他值, 比如这里替换之前的用户名")
context_logger.info("日志文件打印的内容会按照上面的 format 属性来显示, 即 ip user message(指 info() 的内容)")

# 终端输出内容：
2020-12-25 10:39:32.984 | INFO     | __main__:<module>:6 - 上面 bind() 里设置的用户将对应这条信息
2020-12-25 10:39:32.984 | INFO     | __main__:<module>:7 - 可以将参数设置成其他值, 比如这里替换之前的用户名
2020-12-25 10:39:32.984 | INFO     | __main__:<module>:8 - 日志文件打印的内容会按照上面的 format 属性来显示, 即 ip user message(指 info() 的内容)
# 文件输出内容：
127.0.0.1 Alex 上面 bind() 里设置的用户将对应这条信息
127.0.0.1 John 可以将参数设置成其他值, 比如这里替换之前的用户名
127.0.0.1 Alex 日志文件打印的内容会按照上面的 format 属性来显示, 即 ip user message(指 info() 的内容)
```

结合 bind() 和 filter 属性对日志进行更细粒度的控制

```python
# oms_test/log_test.py
from loguru import logger

logger.add('test.log', filter=lambda record: 'special' in record['extra'])
logger.debug('这条 DEBUG 信息不会被记录到日志文件中')
logger.bind(special=True).info('使用 bind() 绑定上面 filter 设置的 special 后会记录消息到日志文件中')

# 终端输出：
2020-12-25 11:08:27.905 | DEBUG    | __main__:<module>:6 - 这条 DEBUG 信息不会被记录到日志文件中
2020-12-25 11:08:27.905 | INFO     | __main__:<module>:7 - 使用 bind() 绑定上面 filter 设置的 special 后会记录消息到日志文件中
# 日志文件输出：
2020-12-25 11:08:27.905 | INFO     | __main__:<module>:7 - 使用 bind() 绑定上面 filter 设置的 special 值后会记录消息到日志文件中
```

### Kafka 的基本使用和单机伪集群搭建

Ubuntu 和 CentOS7 的步骤一样，只不过这里把下载的文件上传到了 CentOS7 中

#### 1. 下载 JDK

本次示例是在 Ubuntu 系统先下载 JDK，然后上传到 CentOS7 云服务器

>下载地址：https://www.oracle.com/java/technologies/javase-jdk15-downloads.html
>
>参考资料：https://blog.csdn.net/lumping/article/details/108552042

```bash
scp -r jdk-15.0.1_linux-x64_bin.tar.gz root@182.254.177.42:/opt
```

登录到云服务器后，查看家目录，发现有该文件了

#### 2. 安装 JDK

```bash
# 把家目录下的压缩文件移至 /opt 目录下
mv jdk-15.0.1_linux-x64_bin.tar.gz /opt
cd /opt
ls
tar -zxvf jdk-15.0.1_linux-x64_bin.tar.gz
ls
```

#### 3. 配置 JDK 环境变量

> 参考资料：https://cloud.tencent.com/developer/article/1558419

```bash
vim /etc/profile
# 添加以下内容，注意路径
export JAVA_HOME=/opt/jdk-15.0.1
export CLASSPATH=.:${JAVA_HOME}/jre/lib/rt.jar:${JAVA_HOME}/lib/dt.jar:${JAVA_HOME}/lib/tools.jar
export PATH=$PATH:${JAVA_HOME}/bin
# 保存退出后激活配置
source /etc/profile
# 查看是否生效
java -version
```

#### 4. 官网下载并解压 kafka

>参考资料：http://kafka.apache.org/quickstart

同样是从 Ubuntu 下载后上传到 CentOS7 中

```bash
# Ubuntu 家目录
scp -r kafka_2.13-2.7.0.tgz root@182.254.177.42:/opt/
ls
# CentOS7
cd /opt
ls
tar -zxvf kafka_2.13-2.7.0.tgz
```

#### 5. 启动 zookeeper 和 kafka

```bash
cd kafka_2.13-2.7.0/
bin/zookeeper-server-start.sh config/zookeeper.properties &
bin/kafka-server-start.sh config/server.properties &
```

#### 6. 创建一个主题 quickstart-events

```bash
bin/kafka-topics.sh --create --topic quickstart-events --bootstrap-server localhost:9092
```

#### 7. 查看新主题的分区数

```bash
bin/kafka-topics.sh --describe --topic quickstart-events --bootstrap-server localhost:9092
```

#### 8. 自主创建生产-消费者模型

```bash
# 生产消息，随便输入几行内容
bin/kafka-console-producer.sh --topic quickstart-events --bootstrap-server localhost:9092
# 消费消息，发现接收到了上面生产者消息
bin/kafka-console-consumer.sh --topic quickstart-events --from-beginning --bootstrap-server localhost:9092
# 这里可以分开两个终端来执行，这样只有生产者发出消息了，消费者就会立即收到该消息
```

#### 10. 删除本地 kafka 环境的任何数据

```bash
# 查看 zookeeper 进程并杀死
ps -ef | grep zookeeper
kill -9 端口号
# 删除临时文件
rm -rf /tmp/kafka-logs /tmp/zookeeper
```

#### 11. 单机伪集群配置

##### 1) 复制两份服务配置文件

```bash
cp config/server.properties config/server-1.properties 
cp config/server.properties config/server-2.properties 
```

##### 2) 修改配置信息

```bash
vim config/server-1.properties 
# 找到下面字段并修改相关属性, 没找到就加进去, 保存退出
broker.id=1
# 允许使用命令删除 topic
delete.topic.enable=true
listeners=PLAINTEXT://127.0.0.1:9093
log.dirs=/tmp/kafka-logs-1

# server-2.properties 文件同理
vim config/server-2.properties 
broker.id=2
delete.topic.enable=true
listeners=PLAINTEXT://127.0.0.1:9094
log.dirs=/tmp/kafka-logs-2
```

##### 3) 启动这两个服务

```bash
# 前面已经杀死了 zookeeper 进程，这里要重启该服务
bin/zookeeper-server-start.sh config/zookeeper.properties &
bin/kafka-server-start.sh config/server-1.properties &
bin/kafka-server-start.sh config/server-2.properties &

# 如果启动时报错如下
kafka.common.InconsistentClusterIdException: The Cluster ID eUIrXKEBRpqak960NpJkTg doesn't match stored clusterId Some(aAs_yU0HSN6GLYkKKwrDlA) in meta.properties. The broker is trying to join the wrong cluster. Configured zookeeper.connect may be wrong.
# 解决办法：杀死所有 zookeeper 端口号
ps -ef | grep zookeeper
kill -9 端口号

# 查看是否还有 zookeeper 和 java 进程
ps -ef | grep zookeeper
ps -ef | grep java
# 删除临时日志文件
rm -rf /tmp/kafka-logs /tmp/kafka-logs-1 /tmp/kafka-logs-2 /tmp/zookeeper

# 重新启动 zookeeper 和 kafka
bin/zookeeper-server-start.sh config/zookeeper.properties &
bin/kafka-server-start.sh config/server-1.properties &
bin/kafka-server-start.sh config/server-2.properties &

# 查看相关端口号
netstat -unltp | grep 909*
tcp6       0      0 127.0.0.1:9093          :::*                    LISTEN      3953/java           
tcp6       0      0 127.0.0.1:9094          :::*                    LISTEN      4387/java
```

##### 4) 创建一个主题 test_topic

```bash
# 因为我们现在开启了两个服务，所以 --replication-factor 对应 2
bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 2 --partitions 1 --topic test_topic
```

##### 5) 查看新主题的分区数

```bash
bin/kafka-topics.sh --describe --zookeeper localhost:2181 --topic test_topic
```

##### 6) 自主创建生产-消费者模型

```bash
# 在 9093 端口生产消息，随便输入几行内容
bin/kafka-console-producer.sh --topic my-replicated-topic --bootstrap-server localhost:9093
# 在 9094 消费消息，发现接收到了上面 9093 端口生产者消息
bin/kafka-console-consumer.sh --topic my-replicated-topic --from-beginning --bootstrap-server localhost:9094
```

##### 7) 删除 test_topic

```bash
bin/kafka-topics.sh --delete --topic test_topic --zookeeper localhost:2181
```

##### 8) 编写一个脚本，方便开机时启动 kafka 服务

```bash
cd
vim kafka.sh
# 输入以下内容，保存退出
#!/bin/sh
cd /opt/kafka_2.13-2.7.0/
sudo bin/zookeeper-server-start.sh config/zookeeper.properties &
sudo bin/kafka-server-start.sh config/server-1.properties &
sudo bin/kafka-server-start.sh config/server-2.properties &
```

### Pykafka 的使用

#### 1. 安装 pykafka

```bash
pip install pykafka
```

#### 2. Pykafka 基本使用示例

##### 1) 查询基础属性值

```python
# oms_test/oms_conf/oms_kafka.py
KAFKA_HOSTS = '127.0.0.1:9093, 127.0.0.1:9094'


# oms_test/oms_test/settings.py
......
# Kafka 配置
KAFKA_HOSTS = oms_kafka.KAFKA_HOSTS
......

# utils 目录下新建目录：kafka
# oms_test/utils/kafka/pykafka_test.py
from pykafka import KafkaClient
from oms_test.settings import KAFKA_HOSTS


class PyKafkaTest:
    """Kafka 基本用法示例"""
    def __init__(self):
        self.hosts = KAFKA_HOSTS
        self.client = KafkaClient(hosts=self.hosts)

    def query(self):
        """查看链接的客户端的各个属性值"""
        # 客户端属性
        print(self.client)
        # <pykafka.client.KafkaClient at 0x7fb3acce0890 (hosts=127.0.0.1:9093, 127.0.0.1:9094)>

        # 查看已创建的节点
        print(self.client.brokers)
        # {
        #     2: <pykafka.broker.Broker at 0x7f6169e0e650 (host=b'127.0.0.1', port=9094, id=2)>,
        #     1: <pykafka.broker.Broker at 0x7f616471b390 (host=b'127.0.0.1', port=9093, id=1)>
        # }
        for broker in self.client.brokers:
            id = self.client.brokers[broker].id
            host = self.client.brokers[broker].host
            port = self.client.brokers[broker].port
            print(f'{id} {host.decode()}:{port}')
        # 2 127.0.0.1:9094
        # 1 127.0.0.1:9093

        # 查看链接的节点
        print(self.client.cluster)
        # <pykafka.cluster.Cluster at 0x7f5fad7aa3d0 (hosts=127.0.0.1:9093, 127.0.0.1:9094)>

        # 查看已有的主题 Topic (假设之前配置 kafka 时所有的主题都被以下命令删除掉了)
        # /opt/kafka_2.13-2.7.0/bin/kafka-topics.sh --delete --topic 主题名 --zookeeper localhost:2181
        print(self.client.topics)
        # {}

        # 上面已经查到没有主题, 所以这里如果输入的主题不存在, 默认自动新建这个主题
        store_topic = self.client.topics['store_topic']
        print(store_topic)
        # <pykafka.topic.Topic at 0x7f47493b4cd0 (name=b'store_topic')>
        print(self.client.topics)
        # {b'store_topic': <weakref at 0x7fb3a5245c50; to 'Topic' at 0x7fb3a53b29d0>}
        

if __name__ == '__main__':
    kafka_obj = PyKafkaTest()
    kafka_obj.query()
```

##### 2) 重复消费示例

```python
# oms_test/tuils/kafka/pykafka_test.py
from pykafka import KafkaClient
from oms_test.settings import KAFKA_HOSTS


class PyKafkaTest:
    """Kafka 基本用法示例"""

    def __init__(self, topic_name=None, consumer_group=None, consumer_id=None):
        self.hosts = KAFKA_HOSTS
        self.client = KafkaClient(hosts=self.hosts)
        self.topic = self.client.topics[topic_name]
        self.consumer_group = consumer_group
        self.consumer_id = consumer_id

    def produce(self):
        """设置一个生产者生产消息"""
        with self.topic.get_sync_producer() as producer:
            # print(producer)  # <pykafka.producer.Producer at 0x7f91eb149310>
            for i in range(5):
                producer.produce(f'测试消息 {i ** 2}'.encode())

    def consume(self):
        """设置一个消费者消费消息"""
        consumer = self.topic.get_simple_consumer()
        # print(consumer)  # <pykafka.simpleconsumer.SimpleConsumer at 0x7f768e032510 (consumer_group=None)>
        for msg in consumer:
            if msg is not None:
                print(f'{msg.offset}, {msg.value.decode()}')


if __name__ == '__main__':
    kafka_obj = PyKafkaTest(topic_name='store_topic', consumer_group=b'first_consumer', consumer_id=b'first')
    kafka_obj.produce()
    kafka_obj.consume()

    
# 运行结果：
0 测试消息 0
1 测试消息 1
2 测试消息 4
3 测试消息 9
4 测试消息 16

# 把 kafka_obj.producer() 注释掉，再多次运行，发现都会有结果，而且结果一样
# 也就是说，我们定义的这个消费者会重复消费主题中的内容
if __name__ == '__main__':
    kafka_obj = PyKafkaTest(topic_name='store_topic', consumer_group=b'first_consumer', consumer_id=b'first')
    # kafka_obj.producer()
    kafka_obj.consumer()
    
# 再把 kafka_obj.producer() 解注释，多次运行发现不但会重复消费，而且会消费新生成的消息
```

##### 3) 不重复消费示例

get_simple_consumer() 如果加了参数，则表示定义了一个具体的消费者

如果该消费者消费了一次 Topic 里的内容，则它不会再消费该 Topic 里面同样的内容

```python
# oms_test/tuils/kafka/pykafka_test.py
from pykafka import KafkaClient
from oms_test.settings import KAFKA_HOSTS


class PyKafkaTest:
    """Kafka 基本用法示例"""

    def __init__(self, topic_name=None, consumer_group=None, consumer_id=None):
        self.hosts = KAFKA_HOSTS
        self.client = KafkaClient(hosts=self.hosts)
        self.topic = self.client.topics[topic_name]
        self.consumer_group = consumer_group
        self.consumer_id = consumer_id

    def produce(self):
        """设置一个生产者生产消息"""
        with self.topic.get_sync_producer() as producer:
            print('生产者开始生产消息 ------>')
            for i in range(5):
                producer.produce(f'测试消息 {i ** 2}'.encode())

    def consume(self):
        """设置一个消费者消费消息"""
        consumer = self.topic.get_simple_consumer(consumer_group=self.consumer_group, auto_commit_interval_ms=1,
                                                  auto_commit_enable=True, consumer_id=self.consumer_id)
        print('消费者开始消费消息 <------')
        for msg in consumer:
            if msg is not None:
                print(f'{msg.offset}, {msg.value.decode()}')


if __name__ == '__main__':
    kafka_obj = PyKafkaTest(topic_name='store_topic', consumer_group=b'first_consumer', consumer_id=b'first')
    kafka_obj.produce()
    kafka_obj.consume()

# 多次运行发现，消费者只会消费生产者生产的最新消息
# 验证方式：把 kafka_obj.producer() 注释掉运行，发现什么消息也没有
# 这就是 get_simple_consumer() 传参的一个特点之一，可以避免同一个消费者重复消费
# 当然，也可以定义另一个消费者，这样就会把之前生产者推送的所有消息都会获取到, 比如：
if __name__ == '__main__':
    kafka_obj = PyKafkaTest(topic_name='store_topic', consumer_group=b'second_consumer', consumer_id=b'second')
    kafka_obj.producer()
    kafka_obj.consumer()
# 运行结果：
生产者开始生产消息 ------>
消费者开始消费消息 <------
0, 测试消息 0
1, 测试消息 1
2, 测试消息 4
3, 测试消息 9
4, 测试消息 16
5, 测试消息 0
6, 测试消息 1
7, 测试消息 4
8, 测试消息 9
9, 测试消息 16
```

### 项目中日志使用示例

#### 1. 配置内容

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
```

#### 2. 项目配置文件

先在项目根目录下新建 log 文件夹

```python
# oms_test/oms_test/settings.py
from oms_conf import oms_db, oms_redis, oms_kafka, oms_log
......
# 日志配置
KAFKA_LOG = oms_log.kafka_log
```

#### 3. kafka 日志使用示例

```python
# oms_test/utils/kafka/pykafka_test.py
import loguru
from pykafka import KafkaClient
from oms_test.settings import KAFKA_HOSTS, KAFKA_LOG
logger = loguru.logger
logger.add(f'{KAFKA_LOG}pykafka_test.log', format='{time} {level} {message}', level='INFO')


class PyKafkaTest:
    """Kafka 基本用法示例"""

    def __init__(self, topic_name=None, consumer_group=None, consumer_id=None):
        self.hosts = KAFKA_HOSTS
        self.client = KafkaClient(hosts=self.hosts)
        self.topic = self.client.topics[topic_name]
        self.consumer_group = consumer_group
        self.consumer_id = consumer_id

    def produce(self):
        """设置一个生产者生产消息"""
        with self.topic.get_sync_producer() as producer:
            logger.info('生产者开始生产消息 ------>')
            for i in range(5):
                producer.produce(f'测试消息 {i ** 2}'.encode())

    def consume(self):
        """设置一个消费者消费消息"""
        consumer = self.topic.get_simple_consumer(consumer_group=self.consumer_group, auto_commit_interval_ms=1,
                                                  auto_commit_enable=True, consumer_id=self.consumer_id)
        logger.info('消费者开始消费消息 <------')
        for msg in consumer:
            if msg is not None:
                logger.info(f'{msg.offset}, {msg.value.decode()}')


if __name__ == '__main__':
    kafka_obj = PyKafkaTest(topic_name='store_topic', consumer_group=b'first_consumer', consumer_id=b'first')
    kafka_obj.produce()
    kafka_obj.consume()

# 运行结果：会生成一个 log 文件，并且 PyCharm 终端内也有消息输出
2021-02-04 13:52:26.930 | INFO     | __main__:producer:21 - 生产者开始生产消息 ------>
2021-02-04 13:52:31.947 | INFO     | __main__:consumer:29 - 消费者开始消费消息 <------
2021-02-04 13:52:31.957 | INFO     | __main__:consumer:32 - 25, 测试消息 0
2021-02-04 13:52:31.957 | INFO     | __main__:consumer:32 - 26, 测试消息 1
2021-02-04 13:52:31.958 | INFO     | __main__:consumer:32 - 27, 测试消息 4
2021-02-04 13:52:31.959 | INFO     | __main__:consumer:32 - 28, 测试消息 9
2021-02-04 13:52:31.960 | INFO     | __main__:consumer:32 - 29, 测试消息 16
2021-02-04 13:52:31.961 | INFO     | __main__:consumer:32 - 30, 测试消息 0
2021-02-04 13:52:31.962 | INFO     | __main__:consumer:32 - 31, 测试消息 1
2021-02-04 13:52:31.963 | INFO     | __main__:consumer:32 - 32, 测试消息 4
2021-02-04 13:52:31.965 | INFO     | __main__:consumer:32 - 33, 测试消息 9
2021-02-04 13:52:31.966 | INFO     | __main__:consumer:32 - 34, 测试消息 16
```

运行该文件，发现 log 目录下有当前日期的目录，里面有 kafka 目录，最里面是 pykafka_test.log

#### 4. 忽略文件添加日志信息

自己本地运行项目时产生的日志文件没必要上传到远程仓库

```bash
# oms_test/.gitignore
.idea/
*.pyc
__pycache__/
oms_conf/
*/migrations/*
api_doc/
log/
```

清理本地 git 缓存

```bash
git rm -r -f --cached .
git add .
git commit -m '日志的基本使用及上传代码时忽略日志文件'
git push origin master
```

### aiokafka 与 kafka-python 库的配合使用

> 参考资料：https://aiokafka.readthedocs.io/en/stable/index.html

- `aiokafka`：一个针对 Kafka 的异步客户端
- `AIOKafkaProducer`：一个高级异步消息生成器
- `AIOKafkaConsumer`：一个高级的异步消息使用者。它与指定的 Kafka 组协调器节点交互，以允许多个使用者负载平衡主题的使用（要求 Kafka >= 0.9.0.0）
- `aiokafka`是使用 [asyncio](http://docs.python.org/3.7/library/asyncio.html) 的 `Apache Kafka` 分布式流处理系统的客户端。它基于 [kafka-python](https://github.com/dpkp/kafka-python) 库，并且将其内部结构重新用于协议解析，错误等。该客户端的设计功能非常类似于官方 `Java` 客户端，并带有大量 Pythonic 接口

#### 1. 安装 asyncio 和 aiokafka

```bash
pip install asyncio
pip install aiokafka
```

#### 2. 简单使用示例

```python
# 在 pykafka_test.py 同目录下新建 kafka_python_test.py 
# oms_test/utils/kafka/kafka_python_test.py
import loguru
import asyncio
from oms_test.settings import KAFKA_LOG, KAFKA_HOSTS
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
logger = loguru.logger
logger.add(f'{KAFKA_LOG}kafka_python_test.log', format='{time} {level} {message}', level='INFO')


class KafkaPythonTest:

    def __init__(self, topic_name=None, group_id=None):
        self.topic_name = topic_name
        self.group_id = group_id
        self.hosts = KAFKA_HOSTS
        self.loop = asyncio.get_event_loop()

    def produce(self):
        """生产者测试"""
        async def producer_obj():
            """定义一个生产者"""
            producer = AIOKafkaProducer(
                loop=self.loop,
                bootstrap_servers=self.hosts
            )
            await producer.start()
            try:
                produce_msg = '实时消息测试'
                # 选择某个主题
                await producer.send_and_wait(self.topic_name, produce_msg.encode())
                logger.info(f'生产者发送消息："{produce_msg}" 成功!')
            except Exception as e:
                logger.info(f'生产者发送消息失败：{e}')
            finally:
                await producer.stop()

        self.loop.run_until_complete(producer_obj())

        return

    def consume(self):
        """消费者测试"""
        async def consumer_obj():
            """定义一个消费者"""
            consumer = AIOKafkaConsumer(
                self.topic_name,
                loop=self.loop,
                bootstrap_servers=self.hosts,
                # 设置一个 group_id, 这样这个消费者只消费一次消息, 不重复消费
                group_id=self.group_id
            )
            await consumer.start()
            try:
                async for msg in consumer:
                    # print(f'consumed: {msg.topic}, {msg.partition}, {msg.offset}, {msg.key}, {msg.value.decode()}, {msg.timestamp}')
                    logger.info(f'消费者接收消息："{msg.value.decode()}" 成功!')
            except Exception as e:
                logger.info(f'消费者接收消息失败：{e}')
            finally:
                await consumer.stop()

        self.loop.run_until_complete(consumer_obj())

        return


if __name__ == '__main__':
    # 注意：因为 kafka 的生产与消费都是实时的, 因此必须先让生产者实时发送一条消息, 这样消费者才能实时接收到
    # 如果不开启生产者发送消息, 消费者会一直等着接收生产者实时发送的消息, 只要生产者不发送消息, 消费者就会一直等着, 不会结束运行
    kafka_obj = KafkaPythonTest(topic_name='store_topic', group_id='first_group')
    kafka_obj.produce()
    kafka_obj.consume()

# 运行结果：
2021-02-04 14:04:17.993 | INFO     | __main__:producer_obj:30 - 生产者发送消息："实时消息测试" 成功!
2021-02-04 14:04:24.246 | INFO     | __main__:consumer_obj:55 - 消费者接收消息："实时消息测试" 成功!
```

#### 3. 高并发时的使用示例

```python

```



#### 4. 项目中 kafka_python 与 MySQL 使用示例

##### 1) MySQL 数据库连接池（Connection pooling）

- 如果所有线程都连接一个 MySQL，那么当它挂掉后，程序也会出现问题。比如在每次执行一个 sql 语句的时候都建立一个 MySQL 连接，执行完就关掉，那么在大数据面前这样频繁开关一个 MySQL 连接，很容易消耗资源，而且容易挂掉

- 而使用数据库连接池则是一个很好的解决办法，它是程序启动时建立足够的数据库连接，并将这些连接组成一个连接池。通过程序动态地对池中的连接进行申请、使用及释放。这样集中管理，供程序使用可以保证较快的数据读写速度，而且不用来回创建数据库的连接，节省时间，也更加安全可靠。简单来说，数据库连接池的优点：减少连接次数，并且支持高并发

##### 2) 安装必要包

```bash
# DBUtils 用来实现数据库连接池的功能，能提升 MySQL 的执行效率
pip install DBUtils
# configparser 用来读取 MySQL 配置文件的内容
# 参考资料：https://www.cnblogs.com/zhou2019/p/10599953.html
# PS：其实可以直接在 oms_db.py 文件里读取 MySQL 配置信息的，这里就当作学习如何读取 MySQL 配置文件内容
pip install configparser
```

##### 3) 新建 MySQL 配置文件

```python
# 1. oms_conf 目录下新建 oms_db.cnf 文件，新增内容：
# 主库配置
[dbMysql]
host=127.0.0.01
port=3306
user=root
password=123456
db_name=oms_test

# 2. utils 目录下新建 mysql 这个 Python 包，里面新建文件：mysql_interface.py
```

