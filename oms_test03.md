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

### kafka 的基本使用和单机伪集群搭建

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

#### 2. 安装 kafka

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

```python
# oms_test/utils/kafka_conf.py
from pykafka import KafkaClient


######## pykafka test ########
# 链接客户端
client = KafkaClient(hosts='127.0.0.1:9093')

# 查看已有的主题 Topic
print(client.topics)
# {b'my-replicated-topic': None}

# 查看已创建的节点
print(client.brokers)
# {
#     2: <pykafka.broker.Broker at 0x7f6169e0e650 (host=b'127.0.0.1', port=9094, id=2)>,
#     1: <pykafka.broker.Broker at 0x7f616471b390 (host=b'127.0.0.1', port=9093, id=1)>
# }
for broker in client.brokers:
    id = client.brokers[broker].id
    host = client.brokers[broker].host
    port = client.brokers[broker].port
    print(f'{id} {host.decode()}:{port}')
# 2 127.0.0.1:9094
# 1 127.0.0.1:9093

# 查看链接的节点
print(client.cluster)
# <pykafka.cluster.Cluster at 0x7f6169dfbc10 (hosts=127.0.0.1:9093)>

# 获取某个主题 Topic
topic = client.topics['my-replicated-topic']
print(topic)
# <pykafka.topic.Topic at 0x7f5ff9696e90 (name=b'my-replicated-topic')>
# 如果输入的主题不存在, 默认自动新建这个主题
new_topic = client.topics['store_topic']
print(new_topic)
# <pykafka.topic.Topic at 0x7f47493b4cd0 (name=b'store_topic')>

# 创建一个同步模式的生产者并推送消息, 只有在确认消息已发送到集群之后, 才会返回调用
with topic.get_sync_producer() as producer:
    for i in range(1, 4):
        producer.produce((f'测试消息 {i ** 2}').encode())

# 创建一个消费者并接收消息
# 注意, 本文件运行多少次就会生产多少次上面的消息并在这里接收到
# 另外, 如果之前我们使用 kafka 测试时随便输入的内容在这里也会接收到
consumer = topic.get_simple_consumer()
print(consumer)
# <pykafka.simpleconsumer.SimpleConsumer at 0x7f768e032510 (consumer_group=None)>
for msg in consumer:
    if msg is not None:
        print(msg.offset, msg.value.decode())
# 0 测试消息 1
# 1 测试消息 4
# 2 测试消息 9
```

> 注意：get_simple_consumer() 如果加了参数，则表示定义了一个具体的消费者
>
> 如果该消费者消费了一次 Topic 里的内容，则它不会再消费该 Topic 里面同样的内容
>
> 验证示例如下：

```python
# oms_test/utils/kafka_conf.py
from pykafka import KafkaClient


client = KafkaClient(hosts='127.0.0.1:9094')
topic = client.topics['test_topic']

consumer = topic.get_simple_consumer(consumer_group=b'first_consume', auto_commit_interval_ms=1, auto_commit_enable=True,consumer_id=b'first')
for msg in consumer:
    if msg is not None:
        print(msg.offset, msg.value.decode())
```

>执行该 py 文件两次，会发现第一次打印消息，第二次以后不再打印，说明没有消费同样的内容
>
>当然，如果生产者推送了新的消息，这个消费者就能再次接收到新的内容，同样只能接收一次

```python
# oms_test/utils/kafka_conf.py
from pykafka import KafkaClient


client = KafkaClient(hosts='127.0.0.1:9094')
topic = client.topics['test_topic']

with topic.get_sync_producer() as producer:
    for i in range(4, 8):
        producer.produce((f'测试消息 {i ** 2}').encode())

consumer = topic.get_simple_consumer(consumer_group=b'first_consume', auto_commit_interval_ms=1, auto_commit_enable=True,consumer_id=b'first')
for msg in consumer:
    if msg is not None:
        print(msg.offset, msg.value.decode())
# 第一次执行结果：
3 测试消息 16
4 测试消息 25
5 测试消息 36
6 测试消息 49
# 第二次执行结果：
7 测试消息 16
8 测试消息 25
9 测试消息 36
10 测试消息 49
......
```

>执行一次上面的内容，发现有打印消息
>
>执行多次，发现 msg.offset 的值越来越大，而每次只会获取生产者最新生成的消息
>
>如果再注释掉生产者代码，执行后发现不会再打印任何消息
>
>这就是 get_simple_consumer() 传参的一个特点之一，可以避免同一个消费者重复消费
>
>如果想重复消费，则不要传任何参数即可

```python
# oms_test/utils/kafka_conf.py
from pykafka import KafkaClient


client = KafkaClient(hosts='127.0.0.1:9094')
topic = client.topics['test_topic']

consumer = topic.get_simple_consumer()
for msg in consumer:
    if msg is not None:
        print(msg.offset, msg.value.decode())
# 不传参多次执行，结果一样(生产者不再推送消息的前提下)
0 测试消息 1
1 测试消息 4
2 测试消息 9
3 测试消息 16
4 测试消息 25
5 测试消息 36
6 测试消息 49
7 测试消息 16
8 测试消息 25
9 测试消息 36
10 测试消息 49
11 测试消息 16
12 测试消息 25
13 测试消息 36
14 测试消息 49
......
```

>当然，也可以定义另一个消费者，这样就会把之前生产者推送的所有消息都会获取到

```python
# oms_test/utils/kafka_conf.py
from pykafka import KafkaClient


client = KafkaClient(hosts='127.0.0.1:9094')
topic = client.topics['test_topic']

consumer = topic.get_simple_consumer(consumer_group=b'second_consume', auto_commit_interval_ms=1, auto_commit_enable=True,consumer_id=b'second')
for msg in consumer:
    if msg is not None:
        print(msg.offset, msg.value.decode())
# 0 测试消息 1
# 1 测试消息 4
# 2 测试消息 9
# 3 测试消息 16
# 4 测试消息 25
# 5 测试消息 36
......
```
