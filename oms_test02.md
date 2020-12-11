[TOC]

### 添加钉钉报警机器人功能

#### 1. 钉钉群添加群机器人

```bash
新建或选择一个钉钉群 -> 点击群机器人 -> 点击自定义 -> 添加 -> 填写机器人名字 -> 点击说明文档可以查看开发者文档 -> 安全设置至少选择一个添加内容 -> 注意：如果选择关键词设置，则消息中至少包含其中一个关键词才可以发送成功 -> 完成 -> 复制 Webhook ->
```

#### 2. 项目中添加钉钉报警 API 示例

```python
import json
import requests
from enum import Enum


class DingDingAPI(object):
    """
    发送钉钉消息
    1.在群里添加自定义机器人
    2.获取到机器人名字 和 url
    """

    class MsgType(Enum):
        text = 'text'
        link = 'link'
        markdown = 'markdown'

    HOOK_MAP = {
        'oms_test': {
            'title': '报警测试',
            # 这里的 url 即对应某个钉钉的某个机器人 url
            'url': 'https://oapi.dingtalk.com/robot/send?access_token=3963e26b849294299817694debeaa76457004d8f98acebc30b54a2579c000685'
        },
    }

    def __init__(self, name):
        _hook = self.HOOK_MAP.get(name)
        self.title, self.url = _hook.get('title'), _hook.get('url')

    @property
    def msg_type(self):
        return self._msg_type

    @msg_type.setter
    def msg_type(self, value):
        if not isinstance(value, self.MsgType):
            raise Exception('{} 必须是 WebHook.MsgType 类型'.format(value))
        self._msg_type = value

    def _send_text(self, msg, at=None, at_all=True, *args, **kwargs):
        """
        发送文本类型消息
        :param msg: 消息内容
        :param at:被@人的手机号(在content里添加@人的手机号) 列表　["156xxxx8827", "189xxxx8325"]
        :param at_all:@所有人时：true，否则为：false
        :return:
        """
        self._data = {
            "msgtype": self.MsgType.text.value,
            "text": {
                "content": '{}警报: {}'.format(self.title, msg)
            },
            "at": {
                "atMobiles": at,
                "isAtAll": at_all
            }
        }

    def _send_link(self, msg, title, message_url, pic_url='', *args, **kwargs):
        """
        发送链接类型消息
        :param msg:消息内容。如果太长只会部分展示
        :param title:消息标题
        :param message_url:点击消息跳转的URL
        :param pic_url:图片URL
        :return:
        """
        self._data = {
            "msgtype": self.MsgType.link.value,
            "link": {
                "text": msg,
                "title": '{}警报: {}'.format(self.title, title),
                "picUrl": pic_url,
                "messageUrl": message_url
            }
        }

    def _send_markdown(self, msg, title=None, at=None, at_all=True, *args, **kwargs):
        """
        发送　markdown格式的消息
        :param msg: markdown格式的消息
        :param title: 首屏会话透出的展示内容
        :param at: 被@人的手机号(在text内容里要有@手机号) 列表　["156xxxx8827", "189xxxx8325"]
        :param at_all: @所有人时：true，否则为：false
        :return:
        """
        self._data = {
            "msgtype": self.MsgType.markdown.value,
            "markdown": {
                "title": '{}警报: {}'.format(self.title, title),
                "text": msg
            },
            "at": {
                "atMobiles": at,
                "isAtAll": at_all
            }
        }

    def send(self, *args, **kwargs):
        send_method = {
            self.MsgType.text: self._send_text,
            self.MsgType.link: self._send_link,
            self.MsgType.markdown: self._send_markdown
        }
        if not self._msg_type:
            raise Exception('请先设置消息类型')
        _send_params = send_method[self._msg_type]
        _send_params(*args, **kwargs)
        res = requests.post(self.url, data=json.dumps(self._data), headers={'Content-Type': 'application/json'}, timeout=10)

        return res.content

if __name__ == '__main__':
    hook = DingDingAPI('oms_test')
    hook.msg_type = hook.MsgType.markdown
    # 这里调用 send() 方法时, 参数里必须包含 "注意" 二字
    # 因为在添加机器人时设置的关键词目前就只有这个
    # r = hook.send('注意：这是一次测试...', at=["15018267752"], atall=False)
    r = hook.send('注意：这是一次测试...', atall=False)
    print(r)
```

### 新增店铺信息

#### 1. 新建 store 子应用

```bash
python manage.py startapp store

# oms_test/oms_test/settings.py
INSTALLED_APPS = [
    ......
    # 自建应用
    'interface_api.apps.InterfaceApiConfig',
    'store.apps.StoreConfig',
]
```

#### 2. 新建 Store 模型类

新建一个抽象基类

```python
# oms_test/utils/base_model
import os, django
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oms_test.settings')
django.setup()
from django.db import models


class BaseModel(models.Model):
    """公共模型类"""

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        # 定义为抽象基类, 表示迁移数据库的时候忽略这个公共模型类
        # 换句话说, 数据库不会创建这个模型类对应的表
        abstract = True
```

新建店铺表

```python
from django.db import models
from utils.base_model import BaseModel

class Store(BaseModel):
    """店铺模型类"""

    STATUS_CHOICES = (
        (0, '关闭弃号'),
        (1, '正常可售'),
        (2, '注册中'),
        (3, '暂时关闭'),
        (4, '注册失败'),
        (5, '假期模式'),
    )
    # 可选择的店铺状态
    usable_status = (1, 3, 5)

    id = models.AutoField(primary_key=True, verbose_name='店铺ID')
    name = models.CharField(max_length=200, blank=True, null=True, verbose_name='店铺名')
    manager_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='店铺负责人')
    manager_id = models.IntegerField(blank=True, null=True, verbose_name='店铺负责人ID')
    center = models.CharField(max_length=100, verbose_name='渠道中心')
    center_id = models.IntegerField(verbose_name='渠道中心ID')
    platform = models.CharField(max_length=45, verbose_name='平台')
    market = models.CharField(max_length=200, null=True, verbose_name='站点')
    market_id = models.IntegerField(null=True, verbose_name='站点ID')
    status = models.SmallIntegerField(choices=STATUS_CHOICES, null=True, verbose_name='状态')
    last_download_time = models.DateTimeField(null=True, blank=True, verbose_name='上次抓单时间')

    class Meta:
        # 告诉 Django 不要管理这个模型类的创建, 修改和删除
        # 想要允许 Django 管理这个模型类的生命周期, 直接删掉它(因为 True 是默认值)
        managed = False
        # 指明该模型类属于 store 这个子应用
        app_label = 'store'
        db_table = 'oms_store'
        verbose_name = verbose_name_plural = '店铺表'
```

#### 3. 迁移数据库

```bash
# 指定只迁移 store 子应用下的模型类
python manage.py makemigrations store
python manage.py migrate

# 点击 Pycharm 的 Database，发现 oms_test 数据库里有一些表
# 但是没有 oms_store 表，因为上面 managed = False 设置限制了
```

#### 4. MySQL 数据库新建 oms_store 表

编写 SQL 语句

> name varchar(200) unique default null comment '店铺名' 
>
> 表示店铺名设置唯一约束，即该表中不能有重复的店铺名

```mysql
create table `oms_store` (
  `id` int(11) not null auto_increment comment '店铺ID',
  `name` varchar(200) unique default null comment '店铺名',
  `manager_name` varchar(100) default null comment '店铺负责人',
  `manager_id` int(11) default null comment '店铺负责人ID',
  `center` varchar(100) default null comment '渠道中心',
  `center_id` int(11) default null comment '渠道中心ID',
  `platform` varchar(45) default null comment '平台名',
  `market` varchar(200) default null comment '站点',
  `market_id` int(11) default null comment '站点ID',
  `status` tinyint(2) default null comment '店铺状态',
  `last_download_time` datetime default null comment '上次抓单时间',
  `create_time` datetime default null comment '创建时间',
  `update_time` datetime default null comment '更新时间',
  primary key (`id`)
) engine=InnoDB default charset=utf8 comment '店铺表';
```

复制上面的 SQL 语句，点击 Pycharm 中 Database 上面的 QL 小图标，选择 'Console(default)'，会自动打开一个窗口：oms_test@localhost[console]

粘贴，将鼠标光标停留在这个语句里的某个位置，左击，然后再点击左上角的绿色三角形按钮即可执行该条 SQL 语句，下方会弹出一个窗口，显示建表过程

#### 5. 批量创建数据（方法一）

```python
# oms_test/store/tests.py
from datetime import datetime
from store.models import Store


def batch_create():
    """批量创建店铺表测试数据"""
    for i in range(1, 200):
        store_dict = dict(
            name=f'test_store_{i}',
            manager_name=f'test_manager_{i}',
            manager_id=i,
            center=f'test_center_{i}',
            center_id=i,
            platform=f'test_platform_{i}',
            market=f'test.{i}.com',
            market_id=i,
            status=1,
            last_download_time=datetime.now(),
            create_time=datetime.now(),
            update_time=datetime.now(),
        )
        print(f'新建数据：{store_dict}')
        Store.objects.create(**store_dict)

    return


if __name__ == '__main__':
    import os, django
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oms_test.settings')
    django.setup()
    batch_create()
```

右键点击 Run 'tests' 即可，但这样创建数据有两个缺点：

1. 如果再次运行该函数，发现数据库会存进重复数据
2. 每次循环都要链接一次数据库，效率很慢，尤其是批量创建数据量大的情况下

#### 6. 批量创建数据（方法二）

在上面 oms_test@localhost[console] 窗口的新建 oms_store 的 SQL 语句下面新增一行 SQL 语句并执行，清空 oms_store 表数据

```mysql
truncate table oms_store;
```

使用 get_or_create() 代替 create() 避免创建重复数据，执行下面 batch_create02 函数

连续多次执行该函数，发现数据库该表始终只有 199 条数据，这就是 get_or_create() 的价值体现之处。另外，看报错内容也可明白，都是提示已经有重复的值了

当然，这并没有解决上面提到的第二个缺点

```python
# oms_test/store/tests.py
from datetime import datetime
from store.models import Store


def batch_create01():
    """批量创建店铺表测试数据（方法一）"""
    for i in range(1, 200):
        store_dict = dict(
            name=f'test_store_{i}',
            manager_name=f'test_manager_{i}',
            manager_id=i,
            center=f'test_center_{i}',
            center_id=i,
            platform=f'test_platform_{i}',
            market=f'test.{i}.com',
            market_id=i,
            status=1,
            last_download_time=datetime.now(),
            create_time=datetime.now(),
            update_time=datetime.now(),
        )
        print(f'新建数据：{store_dict}')
        Store.objects.create(**store_dict)

    return


def batch_create02():
    """批量创建店铺表测试数据（方法二）"""
    for i in range(1, 200):
        store_dict = dict(
            name=f'test_store_{i}',
            manager_name=f'test_manager_{i}',
            manager_id=i,
            center=f'test_center_{i}',
            center_id=i,
            platform=f'test_platform_{i}',
            market=f'test.{i}.com',
            market_id=i,
            status=1,
            last_download_time=datetime.now(),
            create_time=datetime.now(),
            update_time=datetime.now(),
        )
        print(f'新建数据：{store_dict}')
        try:
            Store.objects.get_or_create(**store_dict)
        except Exception as e:
            print(f'新建数据时报错：{e}')
            continue

    return

if __name__ == '__main__':
    import os, django
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oms_test.settings')
    django.setup()
    # batch_create01()
    batch_create02()
```

#### 7. 批量创建数据（方法三）

同理，先清空该表数据

使用 bulk_create() 批量创建，提升效率。

此外，还能避免重复创建数据，可以连续执行多次查看结果

还有一点值得注意：数据库保存的是当前时间的 UTC 时间

```python
# oms_test/store/tests.py
from datetime import datetime
from store.models import Store


def batch_create01():
    """批量创建店铺表测试数据（方法一）"""
    for i in range(1, 200):
        store_dict = dict(
            name=f'test_store_{i}',
            manager_name=f'test_manager_{i}',
            manager_id=i,
            center=f'test_center_{i}',
            center_id=i,
            platform=f'test_platform_{i}',
            market=f'test.{i}.com',
            market_id=i,
            status=1,
            last_download_time=datetime.now(),
            create_time=datetime.now(),
            update_time=datetime.now(),
        )
        print(f'新建数据：{store_dict}')
        Store.objects.create(**store_dict)

    return


def batch_create02():
    """批量创建店铺表测试数据（方法二）"""
    for i in range(1, 200):
        store_dict = dict(
            name=f'test_store_{i}',
            manager_name=f'test_manager_{i}',
            manager_id=i,
            center=f'test_center_{i}',
            center_id=i,
            platform=f'test_platform_{i}',
            market=f'test.{i}.com',
            market_id=i,
            status=1,
            last_download_time=datetime.now(),
            create_time=datetime.now(),
            update_time=datetime.now(),
        )
        print(f'新建数据：{store_dict}')
        try:
            Store.objects.get_or_create(**store_dict)
        except Exception as e:
            print(f'新建数据时报错：{e}')
            continue

    return


def batch_create03():
    """批量创建店铺表测试数据（方法三）"""
    store_list = list()
    for i in range(1, 1000):
        store_dict = dict(
            name=f'test_store_{i}',
            manager_name=f'test_manager_{i}',
            manager_id=i,
            center=f'test_center_{i}',
            center_id=i,
            platform=f'test_platform_{i}',
            market=f'test.{i}.com',
            market_id=i,
            status=1,
            last_download_time=datetime.now(),
            create_time=datetime.now(),
            update_time=datetime.now(),
        )
        # print(f'新建数据：{store_dict}')
        store_list.append(Store(**store_dict))
    # batch_size 表示每次批量处理的数量  ignore_conflicts=True 表示忽略批量创建时的冲突
    Store.objects.bulk_create(store_list, batch_size=200, ignore_conflicts=True)

    return


if __name__ == '__main__':
    import os, django
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oms_test.settings')
    django.setup()
    # batch_create01()
    # batch_create02()
    batch_create03()
```

### Redis 集群

#### 1. CentOS7 下载/安装/启动 Redis 

```bash
# 下载 Redis 包
wget https://download.redis.io/releases/redis-6.0.9.tar.gz
```

#### 2. 安装 Redis

> 参考资料：https://www.cnblogs.com/zuidongfeng/p/8032505.html

```bash
# 安装依赖包
yum install gcc
# 解压
tar -zxvf redis-6.0.9.tar.gz
# 切换到解压后的 Redis 目录
cd redis-6.0.9
# 编译安装
make MALLOC=libc
# 如果报错如下，很有可能是 redis6.0.9 需要的是 gcc5 及以上的版本，但是 CentOS7 系统自带的 gcc 版本是 4.8，所以就要升级一下 gcc 版本
make[1]: *** [server.o] Error 1
make[1]: Leaving directory `/root/redis-6.0.9/src'
make: *** [all] Error 2
# 升级 gcc 版本
sudo yum install centos-release-scl
sudo yum install devtoolset-8-gcc*
scl enable devtoolset-8 bash
gcc -v
# 把 redis-6.0.9 文件夹删除
# 因为刚才编译的时候可能有残余文件，可能导致后面的编译失败
cd ..
rm -rf redis-6.0.9/
tar -zxvf redis-6.0.9.tar.gz
cd redis-6.0.9/
make MALLOC=libc
# 编译后会提示你使用 make test ;)
make test
# 将 src/ 文件夹复制到 /usr/local/bin/ 目录下
cp -r src/ /usr/local/bin/
# 切换到 src 编译安装
cd src/
make install
```

#### 3. 启动 Redis

```bash
# 启动 Redis，这种方式要一直占着窗口，显然不太好
./redis-server
# 按 ctrl+c 关闭，接下来，以后台进程方式启动 Redis
cd ..
ls
vim redis.conf
# 将 daemonize no 改为 daemonize yes，保存退出
# 查看当前绝对路径并复制
pwd
cd src
# 指定 redis.conf 文件启动 
./redis-server /root/redis-6.0.9/redis.conf
# 查看 redis 进程
ps -ef | grep redis
# 发现 Redis 在后台已经启动
```

#### 4. 设置 Redis 开机自动启动

```bash
# 在 /etc 目录下新建 redis 目录
cd /etc
mkdir redis
# 将上面解压后的 Redis 文件夹下的 redis.conf 文件（注意每个人的安装路径可能不一样）复制一份到 /etc/redis 目录下，并命名为6379.conf
cp /root/redis-6.0.9/redis.conf /etc/redis/6379.conf
# 检查是否复制并重命名成功
cd redis/
ls
# 将 Redis 的启动脚本复制一份放到 /etc/init.d 目录下
cp /root/redis-6.0.9/utils/redis_init_script /etc/init.d/redis
# 切换到 init.d 目录下执行自启命令
cd /etc/init.d/
chkconfig redis on
# 如果报错：service redisd does not support chkconfig
# 编辑 /etc/init.d/redis 文件，第一行加入两行注释, 报错并退出
# 注释的意思是：Redis服务必须在运行级 2，3，4，5 下被启动或关闭，启动的优先级是 90，关闭的优先级是 10
# chkconfig:   2345 90 10
# description:  Redis is a persistent key-value database

# PS：Ubuntu 中安装 chkconfig 方法
sudo apt install sysv-rc-conf
sudo cp /usr/sbin/sysv-rc-conf /usr/sbin/chkconfig
```

#### 5. 尝试以服务形式启动和关闭 Redis

```bash
# 开启
service redis start
# 关闭
service redis stop
```

#### 6. 搭建 Redis 集群

> 参考资料：https://www.cnblogs.com/yushangzuiyue/p/9305586.html

```bash
# 我这里将 Redis 解压在家目录下，因此先切换到家目录
# 为方便测试，我把 Redis 集群相关文件也放在家目录下
cd ~
mkdir redis-cluster
cd redis-cluster/
mkdir 7101 7102 7103 7104 7105 7106
# 将上面解压后的 Redis 目录下 src 里的 redis-server 文件复制到这三个目录下
cp /root/redis-6.0.9/src/redis-server 7101/
cp /root/redis-6.0.9/src/redis-server 7102/
cp /root/redis-6.0.9/src/redis-server 7103/
cp /root/redis-6.0.9/src/redis-server 7104/
cp /root/redis-6.0.9/src/redis-server 7105/
cp /root/redis-6.0.9/src/redis-server 7106/
# 在每个新建的目录下新增 redis.conf 文件
vim 7101/redis.conf
# 添加如下内容，7102/7103 的方法一样，对应修改端口就行
port 7101
daemonize yes
# bind 192.168.253.135  # 绑定对外连接提供的 IP
# pidfile 7000.pid  # 进程文件名
cluster-enabled yes
cluster-config-file nodes-7101.conf
cluster-node-timeout 5000
appendonly yes
# 分别启动这三个目录下的 Redis 服务
cd 7101/
./redis-server ./redis.conf
cd ..
cd 7102/
./redis-server ./redis.conf
cd ..
cd 7103/
./redis-server ./redis.conf
# 查看 Redis 服务进程
ps -ef | grep redis-server
root      4821     1  0 15:11 ?        00:00:02 /usr/local/bin/redis-server 127.0.0.1:6379
root     15765     1  0 16:08 ?        00:00:00 ./redis-server *:7101 [cluster]
root     16070     1  0 16:10 ?        00:00:00 ./redis-server *:7102 [cluster]
root     16113     1  0 16:10 ?        00:00:00 ./redis-server *:7103 [cluster]
root     18513     1  0 16:22 ?        00:00:00 ./redis-server *:7104 [cluster]
root     18548     1  0 16:22 ?        00:00:00 ./redis-server *:7105 [cluster]
root     18583     1  0 16:22 ?        00:00:00 ./redis-server *:7106 [cluster]
root     16239 15208  0 16:10 pts/0    00:00:00 grep --color=auto redis-server
# 安装 Ruby
yum install ruby
# 创建 Redis 集群（Ubuntu 貌似不用这一步？）
cd ~
# --cluster-replicas 1 表示从机数量
redis-cli --cluster create 127.0.0.1:7101 127.0.0.1:7102 127.0.0.1:7103 127.0.0.1:7104 127.0.0.1:7105 127.0.0.1:7106 --cluster-replicas 1
# 如果 Redis 版本更低，比如是 4.0 版本的，创建集群命令示例：
# ./redis-trib.rb create --replicas 1 127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005
# 测试进入某个集群点
redis-cli -c -p 7101
# 查看集群信息
127.0.0.1:7101> cluster info
cluster_state:ok
......
# 如果 IP 地址是某个服务器的，这样测试：
redis-cli -c -h 192.168.199.135 -p 7101
# 如果要增加节点，可以这样：
redis-cli --cluster add-node 127.0.0.1:7106 127.0.0.1:7107
```

#### 7. 使用脚本启动 Redis 方法

```bash
# 比如我的 Ubuntu 系统中，Redis 下载安装在家目录下
# 新建一个 sh 文件
vim start_redis.sh
# 添加以下内容，保存退出
#!/bin/sh

cd /home/yanfa/redis-6.0.9/src
./redis-server ../redis.conf
cd /home/yanfa/redis-cluster/7101
./redis-server ./redis.conf
cd /home/yanfa/redis-cluster/7102
./redis-server ./redis.conf
cd /home/yanfa/redis-cluster/7103
./redis-server ./redis.conf
cd /home/yanfa/redis-cluster/7104
./redis-server ./redis.conf
cd /home/yanfa/redis-cluster/7105
./redis-server ./redis.conf
cd /home/yanfa/redis-cluster/7106
./redis-server ./redis.conf

ps -ef | grep redis

# 每次开机后直接执行该文件即可
sh start_redis.sh
# 执行结果：
yanfa     6424  3633  0 17:04 ?        00:00:01 ./redis-server 127.0.0.1:6379
yanfa     6544  3633  0 17:08 ?        00:00:00 ./redis-server *:7101 [cluster]
yanfa     6617  3633  0 17:14 ?        00:00:00 ./redis-server *:7102 [cluster]
yanfa     6623  3633  0 17:14 ?        00:00:00 ./redis-server *:7103 [cluster]
yanfa     6629  3633  0 17:14 ?        00:00:00 ./redis-server *:7104 [cluster]
yanfa     6635  3633  0 17:14 ?        00:00:00 ./redis-server *:7105 [cluster]
yanfa     6641  3633  0 17:14 ?        00:00:00 ./redis-server *:7106 [cluster]
yanfa     6797 31557  0 17:19 pts/22   00:00:00 sh start_redis.sh
yanfa     6813  6797  0 17:19 pts/22   00:00:00 grep redis
```

#### 8. 项目中安装 Redis 和 RedisCluster

```bash
pip install redis
pip install redis-py-cluster
```

#### 9. 配置文件夹 oms_conf 中新增 oms_redis.py 文件

```python
from rediscluster import RedisCluster


class RedisConf:
    """Redis 集群配置"""

    _startup_nodes = [
        {'host': '127.0.0.1', 'port': '7101'},
        {'host': '127.0.0.1', 'port': '7102'},
        {'host': '127.0.0.1', 'port': '7103'},
        {'host': '127.0.0.1', 'port': '7104'},
        {'host': '127.0.0.1', 'port': '7105'},
        {'host': '127.0.0.1', 'port': '7106'},
    ]

    # 链接 Redis 集群
    redis_cluster_conn = RedisCluster(startup_nodes=_startup_nodes, decode_responses=True, skip_full_coverage_check=True)
    

REDIS_CONF = RedisConf()
```

#### 10. 项目中新建一个专门存放对外 API 接口的子应用

```bash
# Pycharm 终端项目根目录下新建子应用
# 因为这里的内容都是接口信息，因此删掉用不上的文件 admin.py/models.py/tests.py
python manage.py startapp interface_api

# 项目配置文件中添加子应用
# oms_test/oms_test/settings.py
INSTALLED_APPS = [
    ......
    # 自建应用
    'interface_api.apps.InterfaceApiConfig',
]
```

#### 11. 安装 rest_framework

```bash
pip install django-rest-framework
```

#### 1. Redis 查询接口

```python
# oms_test/oms_test/settings.py
from oms_conf import oms_db, oms_redis
REDIS_CONF = oms_redis.REDIS_CONF

# oms_test/intercept_api/views.py
```

