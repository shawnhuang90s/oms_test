[TOC]

### Docker 部署 Redis 集群

### Docker 部署 Mysql 主从复制

### Docker 部署 Kafka 

### Docker 部署 Django

### 部署项目到 Docker 容器中 (Ubuntu 系统为例)

#### 1. 项目启动时首页展示

目前启动项目后，没有设置主页路径及对应内容的话，点击该网址跳转到浏览器时会报错

```bash
# 在前面 oms_test01 文件中内容最后有怎么方便启动项目的方法，这里不再提
# 启动后如下：
Performing system checks...
Watching for file changes with StatReloader

System check identified no issues (0 silenced).
January 19, 2021 - 08:06:22
Django version 3.1.3, using settings 'oms_test.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.

# 点击 http://127.0.0.1:8000/，提示 Page not found
# 必须在这个 url 后面再加上 store/ 或者 apidoc/ 之类我们之前已经写好的路径
```

因为现在点击是默认访问主页的，因此我们添加一个简单的东西，不至于出现上面的提示

```python
# oms_test/oms_test/urls.py
from django.views.static import serve
from oms_test.settings import API_DOC_ROOT
from django.http import HttpResponseRedirect
from django.urls import path, include, re_path


def clock_show(request):
    """首页重定向到一个展示个性时钟的网址"""
    return HttpResponseRedirect('http://chabudai.sakura.ne.jp/blogparts/honehoneclock/honehone_clock_tr.swf')


urlpatterns = [
    path('', clock_show),
    path('store/', include(('store.urls', 'store'), namespace='store')),
    re_path('api_doc/(?P<path>.*)', serve, {'document_root': API_DOC_ROOT}),
]
```

重启项目，再点击 http://127.0.0.1:8000/，发现有内容了，OK

#### 2. 生成  requirements.txt 文件

将当前项目所处虚拟环境中安装的所有包到自动生成到该文件

```bash
# PyCharm 终端内，项目根目录下执行
pip freeze > requirements.txt
# 执行后发现项目根目录下自动生成了该文件，可自行打开查看内容
```

#### 2. 项目根目录下新建 dockerfile

先查看 Python 版本

```bash
python3 --version
# 运行结果：
Python 3.7.4
```

PyCharm 终端切换到项目根目录下

```dockerfile
vim Dockerfile
# 添加以下内容：

# 从 Docker 仓库中拉取指定版本的 Python 镜像
FROM python:3.7
# 设置容器中的 Python 环境变量
ENV PYTHONUNBUFFERED 1
# 添加清华镜像源
RUN echo \
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ buster main contrib non-free\
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ buster-updates main contrib non-free\
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ buster-backports main contrib non-free\
deb https://mirrors.tuna.tsinghua.edu.cn/debian-security buster/updates main contrib non-free\
  > /etc/apt/sources.list
# 在容器中新建 code 目录（宿主机不会生成）
RUN mkdir /code
# 将 code 目录设置成工作目录
WORKDIR /code
# 添加 pip 清华镜像源
RUN pip install pip -U -i https://pypi.tuna.tsinghua.edu.cn/simple
# 将宿主机当前目录（即项目根目录）的 requirements.txt 文件复制到容器的 /code 目录下
ADD requirements.txt /code/
# 安装项目中的依赖包（使用清华镜像源）
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 把当前项目根目录下的所有内容复制到容器的 /code 目录下，注意这个点表示复制所有
ADD . /code/
```

#### 3. Docker-compose 的使用

- 在线上环境中，通常不会将项目的所有组件放到同一个容器中
- 更好的做法是把每个独立的功能装进单独的容器，这样方便复用
- 比如将 Django 代码放到容器 A，将 Mysql 数据库放到容器 B，以此类推
- 因此同一个服务器上有可能会运行着多个容器，如果每次都靠一条条指令去启动，未免太繁琐 
- Docker-compose 就是解决这个问题的，它用来编排多个容器，将启动容器的命令统一写到 docker-compose.yml 文件中
- 以后每次启动这一组容器时，只需要使用命令 docker-compose up 就可以

```bash
pip install docker-compose -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install coreapi -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install django-stubs -i https://pypi.tuna.tsinghua.edu.cn/simple
```

查看版本信息

```bash
docker-compose -v
# 运行结果：
docker-compose version 1.28.0, build unknown
```

项目根目录下新建 docker-compose.yml 文件

```yml
# oms_test/docker-compose.yml
# 添加以下内容：

# 版本号, 默认不变
version: "3"
services:
  # app 是一个容器
  app:
    # 除正常工作外, 容器会在任何时候重启, 包括运行遇到bug、进程崩溃、docker 重启等各种情况
    restart: always
    # 指定一个包含 Dockerfile 文件的路径, 并通过此文件构建容器镜像 (这里的 . 代表当前目录)
    build: .
    # 容器运行时执行的命令
    command: "python3 manage.py runserver 0.0.0.0:8000"
    # 卷, 或者说挂载, 容器和宿主机是隔离开的, 但有时候需要联通, 比如代码更新时需要从远程仓库拉取最新代码
    # 这里的卷的配置, 定义了容器与宿主机之间的映射
    # 其中, . 代表宿主机的当前目录, 这里就是项目的根目录; : 为分隔符; /code 表示容器中的目录
    # 简单来说, 宿主机项目根目录与容器内的 /code 目录是联通的, 如果宿主机该目录下的代码变更了, 容器中 /code 目录下的代码也跟着自动变更
    volumes:
      - .:/code
    # 定义宿主机和容器的端口映射, 前提是确保端口没有被其他程序占用
    ports:
      - "8000:8000"
```

使用 docker-compose 启动容器服务

```bash
# PyCharm 终端输入：
docker-compose up
```

### Docker 部署 Redis 集群（Ubuntu为例）[备用]

>参考资料1：https://www.cnblogs.com/sxw123/archive/2004/01/13/14060266.html
>
>参考资料2：https://www.cnblogs.com/sky-chen/p/9810613.html

#### 1. 删除之前已经配置好的 Redis 集群

```bash
sudo rm -rf /opt/redis-6.0.9
sudo rm -rf /etc/redis
```

#### 2. 杀死 Redis 进程

```bash
ps -ef | grep redis
sudo kill -9 redis-server进程ID
sudo kill -9 cluster进程ID
ps -ef | grep redis
```

#### 3. 新建 Redis 集群目录并下载安装 Redis

```bash
mkdir docker_redis_cluster
cd docker_redis_cluster/
wget http://download.redis.io/releases/redis-6.0.9.tar.gz
tar -zxvf redis-6.0.9.tar.gz
cd redis-6.0.9/
make
make test
```

#### 4. 修改 Redis 配置

```bash
vim redis.conf
# 找到以下字段并修改成对应的值，保存退出

# 设置远程访问 Redis 集群
bind 0.0.0.0
# 关闭守护进程
daemonize no
# 设置访问密码
requirepass 123456
# 主从链接密码
masterauth 123456
# 设置日志路径
logfile "/var/log/redis/redis-server.log"
# 配置集群相关字段
cluster-enabled yes
cluster-config-file nodes-6379.conf
cluster-node-timeout 15000
```

#### 5. 新建 Dockerfile

```bash
# 切换到 docker_redis_cluster 目录下，比如我的：
cd /home/yanfa/docker_redis_cluster
# 注意：文件名就叫 Dockerfile，开头大写
vim Dockerfile
# 添加以下内容：

# 这个是我使用的宿主机的 Ubuntu 版本号，注意 Ubuntu 在这里要小写
FROM ubuntu:16.04
# 设置容器中 Redis 路径
ENV REDIS_HOME /usr/local/
# 宿主机的 Redis 源码包复制到镜像的根路径下
# ADD 命令会在复制后自动解包
# 注意：被复制的对象必须与 Dockerfile 在同一目录下(比如这里的 docker_redis_cluster 目录)
# 且 ADD 后面必须使用相对路径
ADD redis-6.0.9.tar.gz /
# 容器中新建目录，用于存放解压 Redis 源码包后的数据文件
RUN mkdir -p $REDIS_HOME/redis
# 复制宿主机当前目录下的 Redis 配置文件到容器中的　/redis 目录
ADD redis-6.0.9/redis.conf $REDIS_HOME/redis/
# 容器中安装编译需要的工具，-y 是安装过程询问是否安装某些内容，如果不加这个参数，过程会中断
RUN apt-get update -y && apt-get install gcc -y && apt-get install make -y
# 容器中切换到 Redis 目录
WORKDIR /redis-6.0.9
# 编译安装 Redis
RUN make
# 复制宿主机当前目录下 Redis 服务文件到容器中相关目录下
RUN mv /redis-6.0.9/src/redis-server $REDIS_HOME/redis/
# 容器中切换到根目录
WORKDIR /
# 容器中删除解压后的目录
RUN rm -rf /redis-6.0.9
# 添加数据卷
VOLUME ["/var/log/redis"]
# 暴露　6379　端口(也可以暴露多个端口)，这里不需要如此
EXPOSE 6379
# 注意：当前镜像非可执行镜像，所以没有包含 ENTRYPOINT 和 CMD 等指令
```

#### 6. 切换 Docker 源

```json
vim /etc/docker/daemon.json
{
  // "registry-mirrors": ["https://5zv3olv1.mirror.aliyuncs.com"]
  "registry-mirrors": ["https://registry.docker-cn.com"]
}
```

#### 7. 构建集群镜像

```bash
# 注意最后这个点不能遗漏
docker build -t my_redis/cluster-redis:6.0.9 .
# 查看是否有该镜像
docker images
```

#### 8. 新建 Redis 节点镜像

```bash
cd
mkdir docker_redis_nodes
cd docker_redis_nodes/
vim Dockerfile
# 添加以下内容：
FROM my_redis/cluster-redis:6.0.9
ENTRYPOINT ["/usr/local/redis/redis-server", "/usr/local/redis/redis.conf"]
```

#### 9. 构建节点镜像并查看

```bash
docker bulid -t my_redis/nodes-redis:6.0.9 .
docker images
```

#### 10. 运行 Redis 容器并查看

```bash
docker run -d --name redis-6379 -p 6379:6379 my_redis/nodes-redis:6.0.9
# 配合项目中的节点端口
docker run -d --name redis-7101 -p 7101:6379 my_redis/nodes-redis:6.0.9
docker run -d --name redis-7102 -p 7102:6379 my_redis/nodes-redis:6.0.9
docker run -d --name redis-7103 -p 7103:6379 my_redis/nodes-redis:6.0.9
docker run -d --name redis-7104 -p 7104:6379 my_redis/nodes-redis:6.0.9
docker run -d --name redis-7105 -p 7105:6379 my_redis/nodes-redis:6.0.9

docker ps
```

#### 11. 链接 Redis 集群查看相关信息

```bash
redis-cli -h 127.0.0.1 -p 6379

127.0.0.1:6379> info replication
NOAUTH Authentication required.

127.0.0.1:6379> auth 123456
OK

127.0.0.1:6379> info replication
# Replication
role:master
connected_slaves:0
master_replid:1fff186ceaf62211f15714c30c6849564dc6da9a
master_replid2:0000000000000000000000000000000000000000
master_repl_offset:0
second_repl_offset:-1
repl_backlog_active:0
repl_backlog_size:1048576
repl_backlog_first_byte_offset:0
repl_backlog_histlen:0

127.0.0.1:6379>exit

# 链接其他端口查看，发现所有的 Redis 都是 master 角色（role:master）
# 显然必须要有主从关系
```

#### 12. 复制各节点的镜像 ID 并查看 IP 地址

```bash
docker ps
# 运行结果如下，复制每个 CONTAINER ID
CONTAINER ID        IMAGE                        COMMAND                  CREATED             STATUS              PORTS                    NAMES
7b105e46c52e        my_redis/nodes-redis:6.0.9   "/usr/local/redis/re…"   6 minutes ago       Up 6 minutes        0.0.0.0:7105->6379/tcp   redis-7105
85a98b81dd3c        my_redis/nodes-redis:6.0.9   "/usr/local/redis/re…"   6 minutes ago       Up 6 minutes        0.0.0.0:7104->6379/tcp   redis-7104
8c74599225c8        my_redis/nodes-redis:6.0.9   "/usr/local/redis/re…"   6 minutes ago       Up 6 minutes        0.0.0.0:7103->6379/tcp   redis-7103
e4da426db5ef        my_redis/nodes-redis:6.0.9   "/usr/local/redis/re…"   6 minutes ago       Up 6 minutes        0.0.0.0:7102->6379/tcp   redis-7102
49a2f14f6cb2        my_redis/nodes-redis:6.0.9   "/usr/local/redis/re…"   6 minutes ago       Up 6 minutes        0.0.0.0:7101->6379/tcp   redis-7101
4f6c6068b1a4        my_redis/nodes-redis:6.0.9   "/usr/local/redis/re…"   6 minutes ago       Up 6 minutes        0.0.0.0:6379->6379/tcp   redis-6379

docker inspect e88a7f3a688b 7b105e46c52e 85a98b81dd3c 8c74599225c8 e4da426db5ef 49a2f14f6cb2 4f6c6068b1a4 | grep IPA
# 运行结果如下，注意每个 IP 对应的端口号
# 7105 端口 IP 地址信息
"SecondaryIPAddresses": null,
"IPAddress": "172.17.0.7",
	"IPAMConfig": null,
	"IPAddress": "172.17.0.7",
# 7104 端口 IP 地址信息
"SecondaryIPAddresses": null,
"IPAddress": "172.17.0.6",
	"IPAMConfig": null,
	"IPAddress": "172.17.0.6",
# 7103 端口 IP 地址信息
"SecondaryIPAddresses": null,
"IPAddress": "172.17.0.5",
	"IPAMConfig": null,
	"IPAddress": "172.17.0.5",
# 7102 端口 IP 地址信息
"SecondaryIPAddresses": null,
"IPAddress": "172.17.0.4",
	"IPAMConfig": null,
	"IPAddress": "172.17.0.4",
# 7101 端口 IP 地址信息
"SecondaryIPAddresses": null,
"IPAddress": "172.17.0.3",
	"IPAMConfig": null,
	"IPAddress": "172.17.0.3",
# 6379 端口 IP 地址信息
"SecondaryIPAddresses": null,
"IPAddress": "172.17.0.2",
	"IPAMConfig": null,
	"IPAddress": "172.17.0.2",
```

#### 13. Redis 集群感知操作

##### 1) 集群相关命令解释

```bash
######## 集群(cluster) ########
# 打印集群的信息
CLUSTER INFO   
# 列出集群当前已知的所有节点（node），以及这些节点的相关信息
CLUSTER NODES 
   
######## 节点(node) ########
# 将 ip 和 port 所指定的节点添加到集群当中，让它成为集群的一份子
CLUSTER MEET <ip> <port>  
# 从集群中移除 node_id 指定的节点
CLUSTER FORGET <node_id>  
# 将当前节点设置为 node_id 指定的节点的从节点
CLUSTER REPLICATE <node_id> 
# 将节点的配置文件保存到硬盘里面
CLUSTER SAVECONFIG 
   
######## 槽(slot) ########
# 将一个或多个槽（slot）指派（assign）给当前节点
CLUSTER ADDSLOTS <slot> [slot ...] 
# 移除一个或多个槽对当前节点的指派
CLUSTER DELSLOTS <slot> [slot ...]  
# 移除指派给当前节点的所有槽，让当前节点变成一个没有指派任何槽的节点
CLUSTER FLUSHSLOTS  
# 将槽 slot 指派给 node_id 指定的节点
# 如果槽已经指派给另一个节点，那么先让另一个节点删除该槽，然后再进行指派
CLUSTER SETSLOT <slot> NODE <node_id>  
# 将本节点的槽 slot 迁移到 node_id 指定的节点中
CLUSTER SETSLOT <slot> MIGRATING <node_id> 
# 从 node_id 指定的节点中导入槽 slot 到本节点
CLUSTER SETSLOT <slot> IMPORTING <node_id> 
# 取消对槽 slot 的导入（import）或者迁移（migrate）
CLUSTER SETSLOT <slot> STABLE 
   
######## 键 (key) ########
# 计算键 key 应该被放置在哪个槽上
CLUSTER KEYSLOT <key> 
# 返回槽 slot 目前包含的键值对数量
CLUSTER COUNTKEYSINSLOT <slot> 
# 返回 count 个 slot 槽中的键
CLUSTER GETKEYSINSLOT <slot> <count> 
```

##### 2) Redis 集群感知：节点握手

```bash
# 指一批运行在集群模式的节点通过 Gossip 协议彼此通信，达到感知对方的过程
# CLUSTER MEET 将 IP 和 PORT 所指定的节点添加到集群当中，让它成为集群的一份子
# 进入 6379 端口对应的 Redis（默认使用它为主节点）
redis-cli -h 127.0.0.1 -p 6379
# 密码认证 
127.0.0.1:6379> auth 123456
OK
# 与上面查到的各节点的 IP 地址进行节点握手
127.0.0.1:6379> cluster meet 172.17.0.3 6379
OK
127.0.0.1:6379> cluster meet 172.17.0.4 6379
OK
127.0.0.1:6379> cluster meet 172.17.0.5 6379
OK
127.0.0.1:6379> cluster meet 172.17.0.6 6379
OK
127.0.0.1:6379> cluster meet 172.17.0.7 6379
OK
# 查看节点信息
127.0.0.1:6379> cluster nodes
2ae13ff294f99c14cb146bc2255a61f828f1baf3 172.17.0.2:6379@16379 myself,master - 0 1611739794000 2 connected
204ba522bc5f09d367725d58fa8d08fede166c3e 172.17.0.3:6379@16379 master - 0 1611739795224 1 connected
479a2d3cac2338303bea7f5086c0f70a8656f0cf 172.17.0.4:6379@16379 master - 0 1611739793217 3 connected
d022cf223a730ff71fd7eec64595c56c56ab5de8 172.17.0.7:6379@16379 master - 0 1611739794221 0 connected
c33d846ced912474a8a5329178114f601fde3f75 172.17.0.6:6379@16379 master - 0 1611739793000 5 connected
4c2396d0547a777dcdd963aa02abb57fee6f35c4 172.17.0.5:6379@16379 master - 0 1611739793000 4 connected
```

##### 3) 查看主节点的槽个数

```bash
# 当前已经使这六个节点组成集群，但是现在还无法工作，因为集群节点还没有分配槽（slot）
127.0.0.1:6379> cluster info
# 运行结果：
# 集群状态：失败，因为没有分配槽位
cluster_state:fail
# cluster_slots_assigned 即被分配的槽个数，目前是 0
cluster_slots_assigned:0
cluster_slots_ok:0
......
127.0.0.1:6379> exit
# 只有全部槽位都分配完成，集群才能正常运行
```

##### 4) 分配槽位

一个槽位只能分配一个节点，16384 个槽位必须分配完，不同节点不能冲突

```bash
# 这里只分配三个节点，终端内执行
# 主节点 IP 地址：127.0.0.1 172.17.0.2
for i in {0..5461};do /usr/local/bin/redis-cli -h 127.0.0.1 -p 6379 -a 123456  CLUSTER ADDSLOTS $i;done
# 从节点1 IP 地址：127.0.0.1 172.17.0.3
for i in {5462..10922};do /usr/local/bin/redis-cli -h 127.0.0.1 -p 7101 -a 123456 CLUSTER ADDSLOTS $i;done
# 从节点2 IP 地址：127.0.0.1 172.17.0.4
for i in {10923..16383};do /usr/local/bin/redis-cli -h 127.0.0.1 -p 7102 -a 123456 CLUSTER ADDSLOTS $i;done
# 查看槽位是否分配完成
redis-cli -h 127.0.0.1 -p 6379
127.0.0.1:6379> auth 123456
OK
127.0.0.1:6379> cluster info
cluster_state:ok
cluster_slots_assigned:16384  # 这里表示都分配好了
cluster_slots_ok:16384
cluster_slots_pfail:0
cluster_slots_fail:0
cluster_known_nodes:6	# 已配置好的节点个数
cluster_size:3	# 已经使用的节点个数
cluster_current_epoch:6
cluster_my_epoch:2
cluster_stats_messages_ping_sent:33
cluster_stats_messages_pong_sent:35
cluster_stats_messages_sent:68
cluster_stats_messages_ping_received:35
cluster_stats_messages_pong_received:30
cluster_stats_messages_received:65
# 查看节点信息命令能更直观查看各个已分配槽位的节点信息
127.0.0.1:6379> cluster nodes
479a2d3cac2338303bea7f5086c0f70a8656f0cf 172.17.0.4:6379@16379 master - 0 1611799873514 3 connected 10923-16383
4c2396d0547a777dcdd963aa02abb57fee6f35c4 172.17.0.5:6379@16379 master - 0 1611799870504 4 connected
2ae13ff294f99c14cb146bc2255a61f828f1baf3 172.17.0.2:6379@16379 myself,master - 0 1611799868000 2 connected 0-5461
204ba522bc5f09d367725d58fa8d08fede166c3e 172.17.0.3:6379@16379 master - 0 1611799871508 1 connected 5462-10922
c33d846ced912474a8a5329178114f601fde3f75 172.17.0.6:6379@16379 master - 0 1611799872000 5 connected
d022cf223a730ff71fd7eec64595c56c56ab5de8 172.17.0.7:6379@16379 master - 0 1611799872512 0 connected

127.0.0.1:6379> exit
```

#### 14. Redis 集群配置高可用性

前面已经搭建了一套完整可运行的 Redis 集群，但目前每个节点都是单点，意味着如果某个节点挂掉了，整个集群会因为槽位分配不完全跟着挂掉。为此，要为每个节点配置备用节点

之前创建了六个节点，集群使用了三个节点，还剩三个可以用来作为备用节点

```bash
# 添加备用节点
# 1.备用节点必须是未分配槽位的，否则会操作失败
# 2.添加格式：链接备用节点 + CLUSTER REPLICATE + 已分配槽位的某个节点
# 3.从上面 cluster nodes 命令运行结果的最右边槽位数可以判断出之前分配了槽位的三个端口的节点（6379/7101/7102）

# 将 7103 端口的节点设置成 6379 端口的备用节点
/usr/local/bin/redis-cli -h 127.0.0.1 -p 7103 -a 123456 CLUSTER REPLICATE 2ae13ff294f99c14cb146bc2255a61f828f1baf3
# 将 7104 端口的节点设置成 7101 端口的备用节点
/usr/local/bin/redis-cli -h 127.0.0.1 -p 7104 -a 123456 CLUSTER REPLICATE 204ba522bc5f09d367725d58fa8d08fede166c3e
# 将 7105 端口的节点设置成 7102 端口的备用节点
/usr/local/bin/redis-cli -h 127.0.0.1 -p 7105 -a 123456 CLUSTER REPLICATE 479a2d3cac2338303bea7f5086c0f70a8656f0cf

# 查看是否配置成功
redis-cli -h 127.0.0.1 -p 6379
127.0.0.1:6379> auth 123456
OK
# 注意看有三个 slave 节点，说明配置成功
127.0.0.1:6379> cluster nodes
479a2d3cac2338303bea7f5086c0f70a8656f0cf 172.17.0.4:6379@16379 master - 0 1611801434000 3 connected 10923-16383
4c2396d0547a777dcdd963aa02abb57fee6f35c4 172.17.0.5:6379@16379 slave 2ae13ff294f99c14cb146bc2255a61f828f1baf3 0 1611801433988 2 connected
2ae13ff294f99c14cb146bc2255a61f828f1baf3 172.17.0.2:6379@16379 myself,master - 0 1611801431000 2 connected 0-5461
204ba522bc5f09d367725d58fa8d08fede166c3e 172.17.0.3:6379@16379 master - 0 1611801434991 1 connected 5462-10922
c33d846ced912474a8a5329178114f601fde3f75 172.17.0.6:6379@16379 slave 204ba522bc5f09d367725d58fa8d08fede166c3e 0 1611801432986 1 connected
d022cf223a730ff71fd7eec64595c56c56ab5de8 172.17.0.7:6379@16379 slave 479a2d3cac2338303bea7f5086c0f70a8656f0cf 0 1611801434000 3 connected

127.0.0.1:6379> exit
```

#### 15. 高可用性测试——故障转移

##### 1) 自动故障转移

```bash
# 停止端口为 7101 的节点容器的运行
docker stop redis-7101
# 再次查看节点信息
redis-cli -h 127.0.0.1 -p 6379
127.0.0.1:6379> auth 123456
OK
# 注意与上面的 cluster nodes 对比，发现，之前 172.17.0.2 对应的端口 7101 节点是 master 身份
# 现在主动停掉该容器的运行后，变成了 slave 身份
# 反过来，上面配置的 7101 节点的备用节点 7104（172.17.0.6）自动变成了 master 身份
# 还有就是我们故意停止了 7101 端口节点容器的运行，它自动变成了 slave 身份后，运行状态也是 fail 状态（172.17.0.3）
127.0.0.1:6379> cluster nodes
479a2d3cac2338303bea7f5086c0f70a8656f0cf 172.17.0.4:6379@16379 master - 0 1611802354412 3 connected 10923-16383
2ae13ff294f99c14cb146bc2255a61f828f1baf3 172.17.0.2:6379@16379 myself,master - 0 1611802354000 2 connected 0-5461
204ba522bc5f09d367725d58fa8d08fede166c3e 172.17.0.3:6379@16379 slave,fail c33d846ced912474a8a5329178114f601fde3f75 1611802318285 1611802316000 7 connected
c33d846ced912474a8a5329178114f601fde3f75 172.17.0.6:6379@16379 master - 0 1611802355414 7 connected 5462-10922
4c2396d0547a777dcdd963aa02abb57fee6f35c4 172.17.0.5:6379@16379 slave 2ae13ff294f99c14cb146bc2255a61f828f1baf3 0 1611802353408 2 connected
d022cf223a730ff71fd7eec64595c56c56ab5de8 172.17.0.7:6379@16379 slave 479a2d3cac2338303bea7f5086c0f70a8656f0cf 0 1611802353000 3 connected

127.0.0.1:6379> exit

# 把 7101 端口对应的节点容器重启，再次查看节点信息
docker restart redis-7101
docker ps
redis-cli -h 127.0.0.1 -p 6379
127.0.0.1:6379> auth 123456
OK
127.0.0.1:6379> cluster nodes
# 运行结果如下，注意 7101 对应的节点还是 slave 身份，但不再是 fail 状态
479a2d3cac2338303bea7f5086c0f70a8656f0cf 172.17.0.4:6379@16379 master - 0 1611804798934 3 connected 10923-16383
2ae13ff294f99c14cb146bc2255a61f828f1baf3 172.17.0.2:6379@16379 myself,master - 0 1611804800000 2 connected 0-5461
204ba522bc5f09d367725d58fa8d08fede166c3e 172.17.0.3:6379@16379 slave c33d846ced912474a8a5329178114f601fde3f75 0 1611804795927 7 connected
c33d846ced912474a8a5329178114f601fde3f75 172.17.0.6:6379@16379 master - 0 1611804799936 7 connected 5462-10922
4c2396d0547a777dcdd963aa02abb57fee6f35c4 172.17.0.5:6379@16379 slave 2ae13ff294f99c14cb146bc2255a61f828f1baf3 0 1611804800939 2 connected
d022cf223a730ff71fd7eec64595c56c56ab5de8 172.17.0.7:6379@16379 slave 479a2d3cac2338303bea7f5086c0f70a8656f0cf 0 1611804799000 3 connected
```

##### 2) 手动故障转移

```bash
# 假设一开始 7101 端口对应的节点容器挂掉了，但它的备用节点 7104 并没有自动升级为 master 身份（即自动故障转移失败的情况）
# 现在肯定进不了 7101 端口的节点
redis-cli -h 127.0.0.1 -p 7101
# 运行结果：
Could not connect to Redis at 127.0.0.1:7101: Connection refused
not connected> exit
# 登录 7104 节点，进行人工故障转移
redis-cli -h 127.0.0.1 -p 7104
127.0.0.1:7104> auth 123456
OK
127.0.0.1:7104> cluster failover
# 运行结果如下，提示要强制进行故障转移
(error) ERR Master is down or failed, please use CLUSTER FAILOVER FORCE
127.0.0.1:7104> cluster failover force
OK
# 再次查看节点信息，发现成功
127.0.0.1:7104> cluster nodes
127.0.0.1:7104> exit
```

#### 16. 访问 Redis 集群测试

```bash
redis-cli -h 127.0.0.1 -p 6379
127.0.0.1:6379> auth 123456
OK
# 添加一个数字，提示要到 IP 地址是 172.17.0.6 对应的节点容器
# 由上面的配置信息得知, 172.17.0.6 对应的节点容器是 7104
# 注意两点：
#   1.其实本来是要到 7101 端口对应的节点容器，因为 6000 > 5462 的槽位，而 0-5462 是在 6379 端口对应的节点容器
#   2.上面操作时把 7101 的主动挂掉，自动故障转移时 7104 的变成了 master 身份，所以这里提示要到 172.17.0.6 对应的节点容器操作
127.0.0.1:6379> set number 6000
(error) MOVED 7743 172.17.0.6:6379
127.0.0.1:6379> exit

# 依据上面提示登录 7104 端口的节点容器
redis-cli -h 127.0.0.1 -p 7104
127.0.0.1:7104> auth 123456
OK
# 添加成功
127.0.0.1:7104> set number 6000
OK
127.0.0.1:7104> get number
"6000"
127.0.0.1:7104> exit

# 尝试在其他端口对应的节点容器获取刚才新存的键 number 对应的值
redis-cli -h 127.0.0.1 -p 7102
127.0.0.1:7102> auth 123456
OK
# 同样提示要登录到 7104 端口才能查看该值
127.0.0.1:7102> get number
(error) MOVED 7743 172.17.0.6:6379
127.0.0.1:7102> exit

# Redis 集群选择某个库
redis-cli -h 127.0.0.1 -p 6379
127.0.0.1:6379> auth 123456
OK
127.0.0.1:6379> select 0
OK
127.0.0.1:6379> select 1
(error) ERR SELECT is not allowed in cluster mode

######## 总结 ########
1. 客户端在初始化的时候只需要知道一个节点的地址即可
2. 客户端会先尝试向这个节点执行命令，比如 get key，如果 key 所在的 slot 刚好在该节点上，则能够直接执行成功
3. 如果 slot 不在该节点，则节点会返回 MOVED 错误，同时把该 slot 对应的节点告诉客户端，客户端可以去该节点执行命令
4. Redis 集群版只使用 0 号库，select 命令只支持 select 0, 输入其他数字报错
```

#### 17. 编写脚本重启 Redis 集群所在容器

```bash
# vim redis.sh
# 添加以下内容：

#!/bin/sh
docker restart redis-6379
docker restart redis-7101
docker restart redis-7102
docker restart redis-7103
docker restart redis-7104
docker restart redis-7105
docker ps
```



