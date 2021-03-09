[TOC]

### MySQL 主从复制（以 CentOS7 为例）

这里为了测试方便，把之前使用的 MySQL 卸载了。现在先在 Ubuntu 系统将文件先下载下来，再上传到远程 CentOS7 系统所在的服务器中

>参考资料：https://www.cnblogs.com/huazai007/articles/11782206.html

#### 1. 下载 MySQL

打开 MySQL 下载页面：https://downloads.mysql.com/archives/community/，选择 5.7.24 版本，下载 mysql-5.7.24-linux-glibc2.12-x86_64.tar.gz 对应的版本

#### 2. 将文件上传到远程服务器

```bash
# 找到刚才存放 MySQL 压缩文件的地方, 复制路径
pwd
cd
# 比如我的是这个路径下 /home/yanfa/Desktop/
scp /home/yanfa/Desktop/mysql-5.7.24-linux-glibc2.12-x86_64.tar.gz root@182.254.177.42:/root/
```

#### 3. 上传后解压

```bash
tar -zxvf mysql-5.7.24-linux-glibc2.12-x86_64.tar.gz -C /usr/local/
# 重命名
mv /usr/local/mysql-5.7.24-linux-glibc2.12-x86_64/ /usr/local/mysql
```

#### 4. 新建 MySQL 数据导入/导出目录

```bash
mkdir -v /usr/local/mysql/mysql-files
```

#### 5. 创建多实例数据目录

```bash
mkdir -vp /data/mysql_data{1..2}
```

#### 6. 给 mysql 用户配置目录权限

```bash
chown -R mysql.mysql /data
chown -R mysql.mysql /usr/local/mysql/
```

#### 7. 编写配置文件

```bash
vim /etc/my.cnf
# 添加以下内容, 保存退出
[mysqld_multi]
mysqld=/usr/local/mysql/bin/mysqld
mysqladmin=/usr/local/mysql/bin/mysqladmin
log=/tmp/mysql_multi.log
user=root
pass=123456

[mysqld]
explicit_defaults_for_timestamp = true
skip-name-resolve

[mysqld1]
# 设置数据目录, 多实例中一定要不同
datadir=/data/mysql_data1
# 设置 sock 存放文件名, 多实例中一定要不同
socket=/tmp/mysql.sock1
# 设置监听开放端口, 多实例中一定要不同
port=3307
# 设置运行用户
user=mysql
# 关闭监控
performance_schema=off
# 设置 innodb 缓存大小
innodb_buffer_pool_size=32M
# 设置监听 IP 地址
bind_address=0.0.0.0
# 关闭 DNS 反向解析
skip-name-resolve=0
# 指定主库 server-id
server-id=101
# bin-log 前缀
log-bin=master
# bin-log-index 前缀
log-bin-index=master-bin.index
# bin-log 格式 (STATEMENT, ROW, FIXED)
# statement：会将对数据库操作的 sql 语句写入到 binlog 中
# row：会将每一条数据的变化写入到 binlog 中
# mixed：statement 与 row 的混合, MySQL 决定什么时候写 statement 格式，什么时候写 row 格式
binlog_format=ROW
# 不需要同步给从库的库
binlog-ignore-db=mysql
binlog-ignore-db=sys
binlog-ignore-db=information_schema
binlog-ignore-db=performance_schema

[mysqld2]
datadir=/data/mysql_data2
socket=/tmp/mysql.sock2
port=3308
user=mysql
performance_schema=off
innodb_buffer_pool_size=32M
bind_address=0.0.0.0
skip-name-resolve=0
server-id=102

# 还有一个参数可以了解一下：
# expire-logs-days　　# bin-log 日志保存天数，保存天数越久占用空间越大
```

#### 8. 初始化实例

```bash
# 初始化完成后自带随机密码在日志中
/usr/local/mysql/bin/mysqld --initialize --user=mysql --basedir=/usr/local/mysql --datadir=/data/mysql_data1
# 运行结果：
2021-01-13T05:55:05.682549Z 0 [Warning] InnoDB: New log files created, LSN=45790
2021-01-13T05:55:05.749310Z 0 [Warning] InnoDB: Creating foreign key constraint system tables.
2021-01-13T05:55:05.823388Z 0 [Warning] No existing UUID has been found, so we assume that this is the first time that this server has been started. Generating a new UUID: e2afe5c7-5563-11eb-ad8e-525400654bb1.
2021-01-13T05:55:05.827785Z 0 [Warning] Gtid table is not ready to be used. Table 'mysql.gtid_executed' cannot be opened.
# 注意这里有提示生成了一个临时密码，记住这个
2021-01-13T05:55:05.830173Z 1 [Note] A temporary password is generated for root@localhost: 6aJSlR#ggMcO
2021-01-13T05:55:07.502154Z 1 [Warning] 'user' entry 'root@localhost' ignored in --skip-name-resolve mode.
2021-01-13T05:55:07.502180Z 1 [Warning] 'user' entry 'mysql.session@localhost' ignored in --skip-name-resolve mode.
2021-01-13T05:55:07.502188Z 1 [Warning] 'user' entry 'mysql.sys@localhost' ignored in --skip-name-resolve mode.
2021-01-13T05:55:07.502200Z 1 [Warning] 'db' entry 'performance_schema mysql.session@localhost' ignored in --skip-name-resolve mode.
2021-01-13T05:55:07.502204Z 1 [Warning] 'db' entry 'sys mysql.sys@localhost' ignored in --skip-name-resolve mode.
2021-01-13T05:55:07.502212Z 1 [Warning] 'proxies_priv' entry '@ root@localhost' ignored in --skip-name-resolve mode.
2021-01-13T05:55:07.502231Z 1 [Warning] 'tables_priv' entry 'user mysql.session@localhost' ignored in --skip-name-resolve mode.
2021-01-13T05:55:07.502235Z 1 [Warning] 'tables_priv' entry 'sys_config mysql.sys@localhost' ignored in --skip-name-resolve mode.


/usr/local/mysql/bin/mysqld --initialize --user=mysql --basedir=/usr/local/mysql --datadir=/data/mysql_data2
# 运行结果：
2021-01-13T05:55:21.422011Z 0 [Warning] InnoDB: New log files created, LSN=45790
2021-01-13T05:55:21.596736Z 0 [Warning] InnoDB: Creating foreign key constraint system tables.
2021-01-13T05:55:21.675665Z 0 [Warning] No existing UUID has been found, so we assume that this is the first time that this server has been started. Generating a new UUID: ec22c372-5563-11eb-b028-525400654bb1.
2021-01-13T05:55:21.679856Z 0 [Warning] Gtid table is not ready to be used. Table 'mysql.gtid_executed' cannot be opened.
# 这里也注意复制这个临时密码
2021-01-13T05:55:21.680305Z 1 [Note] A temporary password is generated for root@localhost: Fiu%a2<fnM5E
2021-01-13T05:55:23.255025Z 1 [Warning] 'user' entry 'root@localhost' ignored in --skip-name-resolve mode.
2021-01-13T05:55:23.255049Z 1 [Warning] 'user' entry 'mysql.session@localhost' ignored in --skip-name-resolve mode.
2021-01-13T05:55:23.255055Z 1 [Warning] 'user' entry 'mysql.sys@localhost' ignored in --skip-name-resolve mode.
2021-01-13T05:55:23.255096Z 1 [Warning] 'db' entry 'performance_schema mysql.session@localhost' ignored in --skip-name-resolve mode.
2021-01-13T05:55:23.255099Z 1 [Warning] 'db' entry 'sys mysql.sys@localhost' ignored in --skip-name-resolve mode.
2021-01-13T05:55:23.255105Z 1 [Warning] 'proxies_priv' entry '@ root@localhost' ignored in --skip-name-resolve mode.
2021-01-13T05:55:23.255122Z 1 [Warning] 'tables_priv' entry 'user mysql.session@localhost' ignored in --skip-name-resolve mode.
2021-01-13T05:55:23.255126Z 1 [Warning] 'tables_priv' entry 'sys_config mysql.sys@localhost' ignored in --skip-name-resolve mode.
```

如果初始化实例时没有显示下面的内容，则查看相关日志文件获取密码信息

```bash
cat /var/log/mysql/error.log | grep "A temporary password is generated"
# 运行结果示例：
2021-01-14T02:55:08.386130Z 1 [Note] A temporary password is generated for root@localhost: T)3&#gIdsgwJ
2021-01-14T02:55:28.967170Z 1 [Note] A temporary password is generated for root@localhost: EUiU#Bs-s0zl
```

#### 9. 复制多实例脚本到服务管理目录下

```bash
cp /usr/local/mysql/support-files/mysqld_multi.server /etc/init.d/mysqld_multi
```

#### 10. 添加脚本权限

```bash
chmod +x /etc/init.d/mysqld_multi
```

#### 11. 添加进 service 服务管理

````bash
chkconfig --add mysqld_multi
````

#### 12. mysqld_multi 多实例管理

```bash
# 查看多实例
/etc/init.d/mysqld_multi report
# 运行结果：
Reporting MySQL servers
MySQL server from group: mysqld1 is not running
MySQL server from group: mysqld2 is not running

# 启动多实例：
/etc/init.d/mysqld_multi start
# 启动某个实例
/etc/init.d/mysqld_multi start 1
# 再次查看多实例
/etc/init.d/mysqld_multi report
# 运行结果：
Reporting MySQL servers
MySQL server from group: mysqld1 is running
MySQL server from group: mysqld2 is running

# 如果上面运行报错
vim /etc/profile
# 添加环境变量，保存退出
export PATH=/usr/local/mysql/bin:$PATH
# 激活
source /etc/profile
```

#### 13. 登录主库实例

```bash
# 注意密码是上面提到的随机生成的密码，复制过来
mysql -uroot -p -S  /tmp/mysql.sock1
# 修改登录密码
SET PASSWORD=PASSWORD('123456');
# 设置密码用不过期
ALTER USER 'root'@'localhost' PASSWORD EXPIRE NEVER;
# 刷新并退出
flush privileges;
exit;
```

#### 14. 关闭主实例的服务 (示例)

```bash
# 重新使用新密码登录，关闭 MySQL 某个实例的服务并刷新
mysql -uroot -p -S  /tmp/mysql.sock1
grant shutdown on *.* to 'root'@'localhost' identified by '123456';
flush privileges;
```

#### 15. 查询主库状态

```bash
show master status\G
# 运行结果如下，记下 File 和 Position 对应的值, 因为需要在从库中设置同步起始值
*************************** 1. row ***************************
             File: master.000001
         Position: 2527
     Binlog_Do_DB: 
 Binlog_Ignore_DB: mysql,sys,information_schema,performance_schema
Executed_Gtid_Set: 
1 row in set (0.00 sec)
```

#### 16. 在主库新建同步用户并退出

```bash
grant replication slave on *.* to 'slave'@'%' identified by '123456';
flush privileges;
exit;
```

#### 17. 登录从库实例

```bash
# 同理复制上面提到的临时密码
mysql -uroot -p -S  /tmp/mysql.sock2
# 修改登录密码
SET PASSWORD=PASSWORD('123456');
# 设置密码用不过期
ALTER USER 'root'@'localhost' PASSWORD EXPIRE NEVER;
# 刷新并退出
flush privileges;
exit;
# 重新使用新密码登录
mysql -uroot -p -S  /tmp/mysql.sock2
# 查询从库状态，发现没有信息
show slave status\G
# 设置从库信息
change master to 
master_host='localhost',
master_user='slave',
master_password='123456',
# 这里的 master_log_file 和 master_log_pos 对应上面主库状态的值
master_log_file='master.000001',
master_log_pos=1163;

# 启动从库服务
start slave;
# 再次查询从库状态
# 如果 Slave_IO_Running 和 Slave_SQL_Running 都是 Yes，表明从库配置成功
show slave status\G
```

#### 18. 查看主从库线程状态

```bash
# 主库
mysql -uroot -p -S  /tmp/mysql.sock1
show processlist\G
# 运行结果：
*************************** 1. row ***************************
     Id: 12
   User: slave
   Host: 127.0.0.1:39900
     db: NULL
Command: Binlog Dump
   Time: 4865
  State: Master has sent all binlog to slave; waiting for more updates
   Info: NULL
*************************** 2. row ***************************
     Id: 20
   User: root
   Host: localhost
     db: NULL
Command: Query
   Time: 0
  State: starting
   Info: show processlist
2 rows in set (0.00 sec)

# 从库
exit;
mysql -uroot -p -S  /tmp/mysql.sock2
show processlist\G
# 运行结果：
*************************** 1. row ***************************
     Id: 8
   User: system user
   Host: 
     db: NULL
Command: Connect
   Time: 4706
  State: Waiting for master to send event
   Info: NULL
*************************** 2. row ***************************
     Id: 9
   User: system user
   Host: 
     db: NULL
Command: Connect
   Time: 1338
  State: Slave has read all relay log; waiting for more updates
   Info: NULL
*************************** 3. row ***************************
     Id: 14
   User: root
   Host: localhost
     db: NULL
Command: Query
   Time: 0
  State: starting
   Info: show processlist
3 rows in set (0.00 sec)
```

#### 19. 测试主从同步是否生效

```bash
# 登录主库新建一个数据库 oms_test
mysql -uroot -p -S  /tmp/mysql.sock1
show databases;
create database oms_test default charset=utf8;
show databases;
exit;

# 登录从库查看是否也有了这个数据库
mysql -uroot -p -S  /tmp/mysql.sock2
show databases;
exit;

# 登录主库新建一张表并插入一条数据
mysql -uroot -p -S  /tmp/mysql.sock1
use oms_test;
show tables;
CREATE TABLE `student` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '学生ID',
  `username` varchar(50) NOT NULL COMMENT '学生名',
  `password` varchar(50) NOT NULL COMMENT '密码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT '学生表';
show tables;
INSERT INTO student (username, password) VALUES ('alex', '12345');
select * from student;
exit;

# 登录从库查看是否也有此表和数据
mysql -uroot -p -S  /tmp/mysql.sock2
use oms_test;
show tables;
select * from student;

# 注意，此时在从库新建一条数据
INSERT INTO student (username, password) VALUES ('Adam', '12345678');
select * from student;
exit;

# 登录主库查看是否也有在从库新增的数据, 发现没有
# 说明是主库的数据同步到从库中，从库的数据不会同步到主库中
mysql -uroot -p -S  /tmp/mysql.sock1
use oms_test;
select * from student;
```

#### 20. 设置主从库读写分离（数据库里直接设置权限）

>参考资料：https://blog.csdn.net/eagle89/article/details/107153687

- 一般来说，设置主从库还要区分各自的使用权限
- 主库拥有所有的权限，而从库一般只用来读取数据即可
- 因为在实际项目中，配置从库的目的是作为一个备份数据
- 并且主从读写分离能够提升项目中对数据使用的效率

##### 1) 设置从库只能执行读操作

```bash
mysql -uroot -p -S  /tmp/mysql.sock2
set global read_only=1;

show global variables like '%read_only%';
# 运行结果
+-----------------------+-------+
| Variable_name         | Value |
+-----------------------+-------+
| innodb_read_only      | OFF   |
| read_only             | ON    |
| super_read_only       | OFF   |
| transaction_read_only | OFF   |
| tx_read_only          | OFF   |
+-----------------------+-------+
5 rows in set (0.00 sec)

# 验证
use oms_test;
INSERT INTO student (username, password) VALUES ('aaa', '12345');
# 运行结果：
Query OK, 1 row affected (0.00 sec)
```

##### 2) 限制 super 用户权限

发现还是能执行插入数据的操作，是因为刚才的设置没生效吗？

并不是，注意 set global read_only=1;  命令只会限制普通用户进行数据修改的权限，但是对具有 super 权限的用户无法限制

刚才我们使用的是 root 用户登录从库的，现在我们用 slave 用户登录进行测试

```bash
mysql -uslave -p -S  /tmp/mysql.sock2
use oms_test;
select * from student;
INSERT INTO student (username, password) VALUES ('bbb', '12345');
# 运行发现报错如下，说明的确限制了普通用户对数据的修改操作
ERROR 1290 (HY000): The MySQL server is running with the --read-only option so it cannot execute this statement
```

要想限制 super 用户在从库修改数据的权限，方法如下

```bash
# 用 root 用户登录从库
mysql -uroot -p -S  /tmp/mysql.sock2
# 将所有表都锁定为只读模式
flush tables with read lock;
# 测试 root 用户能否修改数据
use oms_test;
INSERT INTO student (username, password) VALUES ('bbb', '12345');
# 运行结果如下，说明从库对所有用户都限制了修改数据的操作
ERROR 1223 (HY000): Can't execute the query because you have a conflicting read lock
```

去除数据库针对所有用户只读权限

```bash
# 查看从库所有用户信息
select host,user,authentication_string,plugin from mysql.user\G
# 运行结果：
*************************** 1. row ***************************
                 host: localhost
                 user: root
authentication_string: *6BB4837EB74329105EE4568DDA7DC67ED2CA2AD9
               plugin: mysql_native_password
*************************** 2. row ***************************
                 host: localhost
                 user: mysql.session
authentication_string: *THISISNOTAVALIDPASSWORDTHATCANBEUSEDHERE
               plugin: mysql_native_password
*************************** 3. row ***************************
                 host: localhost
                 user: mysql.sys
authentication_string: *THISISNOTAVALIDPASSWORDTHATCANBEUSEDHERE
               plugin: mysql_native_password
*************************** 4. row ***************************
                 host: %
                 user: slave
authentication_string: *6BB4837EB74329105EE4568DDA7DC67ED2CA2AD9
               plugin: mysql_native_password
4 rows in set (0.00 sec)

# 查看更详细的权限信息
select host,user,authentication_string,plugin,grant_priv,super_priv from mysql.user\G
# 运行结果：
*************************** 1. row ***************************
                 host: localhost
                 user: root
authentication_string: *6BB4837EB74329105EE4568DDA7DC67ED2CA2AD9
               plugin: mysql_native_password
           grant_priv: Y
           super_priv: Y
*************************** 2. row ***************************
                 host: localhost
                 user: mysql.session
authentication_string: *THISISNOTAVALIDPASSWORDTHATCANBEUSEDHERE
               plugin: mysql_native_password
           grant_priv: N
           super_priv: Y
*************************** 3. row ***************************
                 host: localhost
                 user: mysql.sys
authentication_string: *THISISNOTAVALIDPASSWORDTHATCANBEUSEDHERE
               plugin: mysql_native_password
           grant_priv: N
           super_priv: N
*************************** 4. row ***************************
                 host: %
                 user: slave
authentication_string: *6BB4837EB74329105EE4568DDA7DC67ED2CA2AD9
               plugin: mysql_native_password
           grant_priv: N
           super_priv: N
4 rows in set (0.00 sec)

# 解除从库数据只读的限制
unlock tables;

# 测试 root 用户能否再修改数据, 发现可以了
INSERT INTO student (username, password) VALUES ('bbb', '12345');

# 再退出, 使用 slave 用户尝试修改数据
exit;
mysql -uslave -p -S  /tmp/mysql.sock2
use oms_test;
INSERT INTO student (username, password) VALUES ('ccc', '12345');
# 运行结果：
ERROR 1290 (HY000): The MySQL server is running with the --read-only option so it cannot execute this statement
```

总结

1. set global read_only=1; 能够限制该库普通用户对数据的修改操作，但不能限制有 super 权限的用户
2. flush tables with read lock; 会限制所有用户对该库修改数据的操作，包括 super 用户
3. unlock tables; 解除对 super 用户修改数据的限制，但如果没有执行 set global read_only=0; 普通用户仍然不能修改数据
4. 延伸：收回某个用户的 super 权限

```bash
revoke super on *.* from root@'localhost';
show grants for root@'localhost';
```

### MySQL 主从复制（以 Ubuntu 为例）

> 参考资料：https://blog.csdn.net/qq_39123009/article/details/103732208

#### 1. 使用 apt 包管理工具安装

```bash
sudo apt update
sudo apt install mysql-server -y
```

#### 2. 停止 MySQL 服务并禁止其自动启动

```bash
sudo systemctl stop mysql
sudo systemctl disable mysql
```

#### 3. 创建 MySQL 数据存放目录

```bash
sudo mkdir -p /data/mysql/{3306,3307,3308}
```

#### 4. 创建 pid 存放目录

```bash
sudo mkdir -p /data/mysql/pid
```

#### 5. 创建日志文件

```bash
# 创建错误日志记录文件
sudo touch /data/mysql/error.log
```

#### 6. 修改目录权限

```bash
sudo chown -R mysql:mysql /data
```

#### 7. 复制 MySQL 配置文件

```bash
sudo cp /etc/mysql/my.cnf /etc/mysql/3306.cnf
sudo cp /etc/mysql/my.cnf /etc/mysql/3307.cnf
sudo cp /etc/mysql/my.cnf /etc/mysql/3308.cnf
```

#### 8. 编辑三个实例对应的配置文件

3306.cnf

```bash
sudo vim /etc/mysql/3306.cnf
# 添加以下内容：
[mysqld]
port=3306
datadir=/data/mysql/3306/
socket=/tmp/mysql3306.sock
symbolic-links=0

[mysqld_safe]
log-error=/data/mysql/3306.log
pid-file=/data/mysql/pid/3306.pid

[client]
port=3306
socket=/tmp/mysql3306.sock
```

3307.cnf

```bash
sudo vim /etc/mysql/3307.cnf
# 添加以下内容：
[mysqld]
port=3307
datadir=/data/mysql/3307/
socket=/tmp/mysql3307.sock
symbolic-links=0

[mysqld_safe]
log-error=/data/mysql/3307.log
pid-file=/data/mysql/pid/3307.pid

[client]
port=3307
socket=/tmp/mysql3307.sock
```

3308.cnf

```bash
sudo vim /etc/mysql/3307.cnf
# 添加以下内容：
[mysqld]
port=3308
datadir=/data/mysql/3308/
socket=/tmp/mysql3308.sock
symbolic-links=0

[mysqld_safe]
log-error=/data/mysql/3308.log
pid-file=/data/mysql/pid/3308.pid

[client]
port=3308
socket=/tmp/mysql3308.sock
```

#### 9. 修改 MySQL 配置文件

```bash
sudo vim /etc/mysql/my.cnf
# 添加以下内容：
[mysqld_multi]
mysqld=/usr/bin/mysqld_safe
mysqladmin=/usr/bin/mysqladmin
user=root
# 需要注意，是 pass 而不是 password，用于后面使用 stop 时使用，可修改为你自定义的密码
pass=123456

[mysqld3306]
port=3306
server-id=3306
datadir=/data/mysql/3306/
log-bin=/data/mysql/3306/mysql-bin
pid-file=/data/mysql/pid/3306.pid
socket=/tmp/mysql3306.sock
log-error=/data/mysql/error.log
skip-external-locking

[mysqld3307]
port=3307
server-id=3307
datadir=/data/mysql/3307/
log-bin=/data/mysql/3307/mysql-bin
pid-file=/data/mysql/pid/3307.pid
socket=/tmp/mysql3307.sock
log-error=/data/mysql/error.log
skip-external-locking

[mysqld3308]
port=3308
server-id=3308
datadir=/data/mysql/3308/
log-bin=/data/mysql/3308/mysql-bin
pid-file=/data/mysql/pid/3308.pid
socket=/tmp/mysql3308.sock
log-error=/data/mysql/error.log
skip-external-locking

[mysql]
no-auto-rehash
# 为了配置 Django 项目中链接数据库进行访问，这里选择 3306 这个主库作为 MySQL 默认链接的库
# 也就是说在终端输入 mysql -uroot -p 登录时，默认登录的是主库
# 如果不加这个 socket 配置，后面主从复制配置成功后如果尝试 mysql -uroot -p 登录时
# 会直接报错：Can't connect to local MySQL server through socket '/var/run/mysqld/mysqld.sock'
socket=/tmp/mysql3306.sock
```

#### 10. 授权 mysqld 目录访问权限

```bash
sudo vim /etc/apparmor.d/usr.sbin.mysqld
# 大括号里添加以下内容：
/data/mysql/ r,
/data/mysql/** rwk,

# 重启 apparmor 服务
sudo service apparmor restart
```

#### 11. 初始化 3306/3307/3308 这三个实例

```bash
sudo mysqld --defaults-file=/etc/mysql/3306.cnf --initialize-insecure --user=mysql --explicit_defaults_for_timestamp
sudo mysqld --defaults-file=/etc/mysql/3307.cnf --initialize-insecure --user=mysql --explicit_defaults_for_timestamp
sudo mysqld --defaults-file=/etc/mysql/3308.cnf --initialize-insecure --user=mysql --explicit_defaults_for_timestamp
```

#### 12. 修改目录权限

```bash
sudo chown -R <本机用户名>:root /data
```

#### 13. 启动运行三个实例并查看

```bash
# 启动
mysqld_multi start 3306-3308
# 查看实例运行状态
mysqld_multi report
# 查看端口信息
netstat -lnpt | grep -E "3306|3307|3308"
```

#### 14. 设置三个实例的登录密码

```bash
# 因为在前面初始化数据库时使用的是 –initialize-insecure 参数
# 所以默认的数据库时没有密码的，我们通过 mysqladmin 命令初始化
mysqladmin -u root password 123456 -S /tmp/mysql3306.sock
mysqladmin -u root password 123456 -S /tmp/mysql3307.sock
mysqladmin -u root password 123456 -S /tmp/mysql3308.sock

# 或者
mysqladmin -u root password 123456 -P3306 -h127.0.0.1
mysqladmin -u root password 123456 -P3307 -h127.0.0.1
mysqladmin -u root password 123456 -P3308 -h127.0.0.1
```

如果后续要修改密码，示例命令如下

```bash
mysqladmin -u root -p password <新密码> -P3306 -h127.0.0.1
# 回车后输入数据库旧密码确认即可
```

#### 15. 登录实例

```bash
mysql -u root -p -S /tmp/mysql3306.sock
```

#### 16. 设置允许远程链接数据库

```mysql
# '%'表示允许任何 IP 访问
update mysql.user set host='%' where user='root';
# 刷新
flush privileges;
# 查看是否修改成功
select user, host from mysql.user;
exit;
```

#### 17. 解除数据库默认绑定的 IP 地址限制

```bash
sudo vim /etc/mysql/mysql.conf.d/mysqld.cnf
# 将 bind-address = 127.0.0.1 这一行注释掉
```

#### 18. 重启各个实例

```bash
mysqld_multi stop 3306-3308
mysqld_multi start 3306-3308

# 查看端口信息
netstat -lnpt | grep -E "3306|3307|3308"
```

#### 19. 设置 3306 端口作为主库

```bash
mysql -u root -p -S /tmp/mysql3306.sock
GRANT REPLICATION SLAVE ON *.* TO 'slave1'@'localhost' IDENTIFIED BY 'slave1';
GRANT REPLICATION SLAVE ON *.* TO 'slave2'@'localhost' IDENTIFIED BY 'slave2';
flush privileges;
# 查看主库状态, 记住 File 和 Position 的值
show master status\G
exit;
# 注意：执行完此步骤后不要再操作主服务器 MySQL，防止主服务器状态发生状态值变化
```

#### 20. 设置 3307/3308 端口作为从库

##### 1) 3307 从库设置

```bash
# 登录 3307 从库
mysql -u root -p -S /tmp/mysql3307.sock
# 注意：这里的 master_log_file 和 master_log_position 分别对应上面 File 和 Position 的值
change master to master_host='localhost', master_user = 'slave1', master_password = 'slave1', master_log_file = 'mysql-bin.000002', master_log_pos = 876;
# 开启 Slave 模式
start slave;
# 查看 Slave 状态
show slave status\G
exit;
```

##### 2) 3308 从库设置

```bash
# 登录 3308 从库
mysql -u root -p -S /tmp/mysql3308.sock
# 注意：这里的 master_log_file 和 master_log_position 分别对应上面 File 和 Position 的值
change master to master_host='localhost', master_user = 'slave2', master_password = 'slave2', master_log_file = 'mysql-bin.000002', master_log_pos = 876;
# 开启 Slave 模式
start slave;
# 查看 Slave 状态
show slave status\G
exit;
```

##### 3) 查询相关状态

```bash
# 如果查看两个从库的状态时，以下信息状态对应，说明 Slave 正常运行
Slave_IO_State:Waiting for master ot send event
Slave_IO_Running: YES
Slave_SQL_Running: YES
```

#### 21. 测试主从复制是否成功

```bash
# 登录主库新建一个数据库
mysql -u root -p -S /tmp/mysql3306.sock
create database oms_test default charset=utf8;
exit;
# 登录从库查询是否也有该数据库
mysql -u root -p -S /tmp/mysql3307.sock
show databases;
exit
mysql -u root -p -S /tmp/mysql3308.sock
show databases;
exit
```

#### 22. 常用语句总结

```bash
show master status;  # 查看 master 的状态，尤其是当前的日志及位置
show slave status;   # 查看 slave 的状态
start slave;         # 启动 slave 模式
stop slave;          # 停止 slave 模式
```

### 项目中配置 MySQL 主从复制与读写分离

#### 1. 数据库主从复制与读写分离配置

```bash
# oms_test/oms_conf/oms_db.py
#!/usr/bin/env python
# encoding: utf-8

# 数据库配置
DATABASES = {
    # 主库
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'NAME': 'oms_test',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': 3306,
    },
    # 这里只配置 3307 端口作为从库查数据
    'slave': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'NAME': 'oms_test',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': 3308,
    },
}


class MasterSlaveDBRouter(object):
    """MySQL 数据库主从复制读写分离路由配置"""

    def db_for_read(self, model, **hints):
        """读数据库"""
        return 'slave'

    def db_for_write(self, model, **hints):
        """写数据库"""
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """是否运行关联操作"""
        return True
```

#### 2. 项目配置文件添加 MySQL 配置内容

```python
# oms_test/oms_test/settings.py

......
DATABASES = oms_db.DATABASES
# 配置读写分离
DATABASE_ROUTERS = ['oms_conf.oms_db.MasterSlaveDBRouter']
......
```

#### 3. PyCharm 中 Database 重新链接

- 前面项目中使用 MySQL 时，没有进行主从复制和读写分离配置
- 这里配置好后，点击 PyCharm 右边的 Database，右击选中之前链接的数据库，点击 remove
- 点击 + 号重新链接主库 ---> Host：127.0.0.1 ---> Database：oms_test ---> User：root ---> Password：123456 ---> 点击 Test Connection，没问题后点击 Apply ---> 点击 OK
- 链接后，发现里面只有我们刚才主从复制测试新建的那个 oms_test 数据库

#### 4. 重新迁移项目数据库并添加测试数据

先删除 store/user 目录下 的 makemigrations 文件夹，然后执行命令：

```bash
python manage.py makemigrations user
python manage.py makemigrations store
python manage.py migrate
```

运行后，Database 里右击点击我们刚才链接的数据库，即 oms_test@localhost，点击上方的刷新按钮，刷新数据库，再点击该数据库，查看详情，发现多了 Django 自带的一些表。当然，oms_store 和 oms_user 表是不会迁移的，因为一开始设置了 managed = False

再次点击 oms_test@localhost，点击 `QL` 按钮，复制 oms_table.sql 文件中的建表语句，重新执行一遍

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

点击刷新按钮，再次查看，发现数据库中多了这两个表

打开 oms_test/store/tests.py 文件，右击重新运行该文件，添加测试店铺数据，再查看该表，发现数据有了

#### 5. 验证主从复制是否成功

```bash
# 打开 PyCharm 终端，进入主/从库查看是否有了上面新增的表和数据

# 使用默认方式登录
mysql -uroot -p
# 切换到 oms_test 数据库
mysql> use oms_test;
Database changed
mysql> show tables;
+----------------------------+
| Tables_in_oms_test         |
+----------------------------+
| auth_group                 |
| auth_group_permissions     |
| auth_permission            |
| auth_user                  |
| auth_user_groups           |
| auth_user_user_permissions |
| django_admin_log           |
| django_content_type        |
| django_migrations          |
| django_session             |
| oms_store                  |
| oms_user                   |
+----------------------------+
12 rows in set (0.00 sec)

mysql> select * from oms_store order by id desc limit 5;
+-----+----------------+------------------+------------+-----------------+-----------+-------------------+--------------+-----------+--------+---------------------+
| id  | name           | manager_name     | manager_id | center          | center_id | platform          | market       | market_id | status | last_download_time  |
+-----+----------------+------------------+------------+-----------------+-----------+-------------------+--------------+-----------+--------+---------------------+
| 199 | test_store_199 | test_manager_199 |        199 | test_center_199 |       199 | test_platform_199 | test.199.com |       199 |      1 | 2021-01-18 07:45:06 |
| 198 | test_store_198 | test_manager_198 |        198 | test_center_198 |       198 | test_platform_198 | test.198.com |       198 |      1 | 2021-01-18 07:45:06 |
| 197 | test_store_197 | test_manager_197 |        197 | test_center_197 |       197 | test_platform_197 | test.197.com |       197 |      1 | 2021-01-18 07:45:06 |
| 196 | test_store_196 | test_manager_196 |        196 | test_center_196 |       196 | test_platform_196 | test.196.com |       196 |      1 | 2021-01-18 07:45:06 |
| 195 | test_store_195 | test_manager_195 |        195 | test_center_195 |       195 | test_platform_195 | test.195.com |       195 |      1 | 2021-01-18 07:45:06 |
+-----+----------------+------------------+------------+-----------------+-----------+-------------------+--------------+-----------+--------+---------------------+
5 rows in set (0.00 sec)

mysql> exit;
Bye

# 同理使用同样的 sql 语句查看主库/从库的数据
mysql -uroot -p -S /tmp/mysql3306.sock
......
mysql -uroot -p -S /tmp/mysql3307.sock
......
mysql -uroot -p -S /tmp/mysql3308.sock
......
```

#### 6. 虚拟环境安装 ipython 

>`ipython`是一个`python`的交互式`shell`，比默认的`python shell`好用得多，支持变量自动补全，自动缩进，支持`bash shell`命令，内置了许多很有用的功能和函数
>
>最主要的是，在 Django 项目中，可以在这个 shell 里面调用当前项目的 models.py 中的 API，对于操作数据非常方便

没安装前，查看 `python shell` 使用效果

```bash
# 打开 PyCharm 终端
python manage.py shell

# 执行结果，如果想复制某段代码块来查看执行效果，会非常麻烦，进行出现缩进问题
Python 3.7.4 (default, Aug  4 2020, 15:26:49) 
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from store.models import Store
>>> exit()
```

安装 `ipython` 和 `jedi`

```bash
# 如果默认安装最新版本，可能报错，因此这里指定某个版本
pip install ipython==7.13.0 -i https://pypi.douban.com/simple/
pip install jedi==0.17.0 -i https://pypi.douban.com/simple/
```

使用 `ipython` 

```python
python manage.py shell

# 运行内容示例：
from store.models import Store
r = Store.objects.all()
r
# 运行结果：
Out[3]: <QuerySet [<Store: Store object (1)>, <Store: Store object (2)>, <Store: Store object (3)>, <Store: Store object (4)>, <Store: Store object (5)>, <Store: Store object (6)>, <Store: Store object (7)>, <Store: Store object (8)>, <Store: Store object (9)>, <Store: Store object (10)>, <Store: Store object (11)>, <Store: Store object (12)>, <Store: Store object (13)>, <Store: Store object (14)>, <Store: Store object (15)>, <Store: Store object (16)>, <Store: Store object (17)>, <Store: Store object (18)>, <Store: Store object (19)>, <Store: Store object (20)>, '...(remaining elements truncated)...']>
```

#### 7. 模型类中使用 `__str__` 

这里发现，每条数据的显示格式都是 <Store: Store object (1)>，看不出是什么内容，为了更直观查看每个店铺的店铺名，可以在模型类中设置

```python
# oms_test/store/models.py
from django.db import models


class Store(models.Model):
    """店铺模型类"""
    ......
    # 添加以下内容
    def __str__(self):
        return self.name
```

终端退出 shell 并重新进入，查看效果

```python
python manage.py shell

# 再次执行
from store.models import Store
r = Store.objects.all()
r
# 这里发现之前的 <Store: Store object (1)> 变成了 <Store: test_store_1>，一下子就能看出是什么店铺
Out[3]: <QuerySet [<Store: test_store_1>, <Store: test_store_2>, <Store: test_store_3>, <Store: test_store_4>, <Store: test_store_5>, <Store: test_store_6>, <Store: test_store_7>, <Store: test_store_8>, <Store: test_store_9>, <Store: test_store_10>, <Store: test_store_11>, <Store: test_store_12>, <Store: test_store_13>, <Store: test_store_14>, <Store: test_store_15>, <Store: test_store_16>, <Store: test_store_17>, <Store: test_store_18>, <Store: test_store_19>, <Store: test_store_20>, '...(remaining elements truncated)...']>
```

之前我们在 oms_user 表其实使用了 `__str__`，只不过没有查看实际效果

```python
# oms_test/user/models.py
......
class User(models.Model):
    ......
    def __str__(self):
        # 优先显示用户名, 其次是ID
        return str(self.username) or str(self.id)
```

#### 8. 项目启动时报错 MySQL 无法链接解决办法

```bash
# 场景：重启电脑后，再尝试重启项目时发现报错：
django.db.utils.OperationalError: (2003, "Can't connect to MySQL server on '127.0.0.1' ([Errno 111] Connection refused)")

# 终端尝试链接 MySQL 
mysql -uroot -p
# 报错：
ERROR 2002 (HY000): Can't connect to local MySQL server through socket '/tmp/mysql3306.sock' (2)

# 查看 MySQL 服务状态
ps -ef | grep mysql
# 结果如下，发现没有运行
yanfa    19135  5505  0 14:46 pts/18   00:00:00 grep --color=auto mysql

# 尝试重新启动 MySQL
systemctl start mysql
# 报错：
Job for mysql.service failed because the control process exited with error code. See "systemctl status mysql.service" and "journalctl -xe" for details.

# 根据提示查看 MySQL 状态
systemctl status mysql.service
# 红字提示：
Failed to start MySQL Community Server.

# 后来想起，可能是之前创建的三个实例关机后也自动关闭了，再次尝试启动三个实例
mysqld_multi start 3306-3308
# 查看结果：
mysqld_multi report
# 运行结果：
Wide character in print at /usr/bin/mysqld_multi line 678.
Reporting MySQL servers
MySQL server from group: mysqld3306 is running
MySQL server from group: mysqld3307 is running
MySQL server from group: mysqld3308 is running

# 再次尝试登录 MySQL，发现可以了
mysql -uroot -p

# 顺便像之前的 Redis 和 Kafka 一样，新建一个 sh 文件
vim mysql.sh
# 添加以下内容，保存退出
#!/bin/sh
mysqld_multi start 3306-3308
mysqld_multi report
netstat -lnpt | grep -E "3306|3307|3308"
```

