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
  primary key (`id`)
) engine=InnoDB default charset=utf8 comment '店铺表';