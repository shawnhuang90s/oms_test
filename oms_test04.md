[TOC]

### MySQL 主从复制

#### 1. 安装依赖包

> 参考资料：https://my.oschina.net/xiaowangqiongyou/blog/1808561

```bash
# 检查系统中是否已安装
rpm -qa | grep cmake
# 如果没有版本信息, 安装
yum -y install cmake
# 下面几个一样，没有就安装，安装命令：yum -y install 包名
rpm -qa | grep make
rpm -qa | grep gcc
rpm -qa | grep gcc-c++
rpm -qa | grep ncurses-devel
rpm -qa | grep bison
```

