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
password=123456

[mysqld]
explicit_defaults_for_timestamp = true
skip-name-resolve

[mysqld1]
# 设置数据目录, 多实例中一定要不同
datadir=/data/mysql_data1
# 设置 sock 存放文件名, 多实例中一定要不同
socket=/tmp/mysql.sock1
# 设置监听开放端口, 多实例中一定要不同
port=3306
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
port=3307
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
vim /etc/profile
# 添加环境变量，保存退出
export PATH=/usr/local/mysql/bin:$PATH
# 激活
source /etc/profile

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

#### 14. 关闭主实例的服务

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
mysql> change master to 
-> master_host='localhost',
-> master_user='slave',
-> master_password='123456',
# 这里的 master_log_file 和 master_log_pos 对应上面主库状态的值
-> master_log_file='master.000001',
-> master_log_pos=1163;
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

