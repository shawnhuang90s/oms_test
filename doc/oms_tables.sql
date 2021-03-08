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
  `date_joined` datetime DEFAULT NULL COMMENT '新建用户加入时间记录',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT '用户表';


CREATE TABLE `student` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '学生ID',
  `username` varchar(50) NOT NULL COMMENT '学生名',
  `password` varchar(50) NOT NULL COMMENT '密码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT '学生表';


CREATE TABLE `oms_permission_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '权限接口详情ID',
  `api_url_address` varchar(256) DEFAULT NULL COMMENT '接口地址',
  `request_method` varchar(10) DEFAULT NULL COMMENT '请求方式',
  `permission_name` varchar(128) DEFAULT NULL COMMENT '权限名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE (`api_url_address`, `request_method`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT '权限接口详情表';


CREATE TABLE `oms_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '查看/操作权限ID',
  `api_name` varchar(64) DEFAULT NULL COMMENT '界面模块',
  `permission_list` varchar(64) DEFAULT NULL COMMENT '权限ID组合',
  `executor` varchar(64) DEFAULT NULL COMMENT '执行人',
  `operator` varchar(64) DEFAULT NULL COMMENT '操作人',
  `permission_type` tinyint(2) DEFAULT 0 COMMENT '权限类型',
  `is_active` tinyint(2) DEFAULT 0 COMMENT '是否启用(默认启用)',
  `category` tinyint(2) DEFAULT 0 COMMENT '模块类别',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT '查看/操作权限表';


CREATE TABLE `oms_permission_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '查看/操作权限记录ID',
  `before_change` tinyint(2) DEFAULT NULL COMMENT '被修改之前的状态',
  `after_change` tinyint(2) DEFAULT NULL COMMENT '被修改之后的状态',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id`) REFERENCES oms_permission(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT '查看/操作权限记录表';