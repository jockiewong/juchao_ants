"""股票公告事件追踪
表结构:
CREATE TABLE `sf_secu_announcement_detail` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `InnerCode` int(10) DEFAULT NULL COMMENT '股票内部编码',
  `SecuCode` varchar(100) NOT NULL COMMENT '股票代码',
  `EventCode` varchar(100) NOT NULL COMMENT '事件代码',
  `PubDate` datetime NOT NULL COMMENT '发布日期',
  `PubDatetime` datetime NOT NULL COMMENT '发布时间(精确到秒)(与PubDate字段不冲突)',
  `NewsNum` int(11) NOT NULL COMMENT '新闻转载次数',
  `PostNum` int(11) NOT NULL COMMENT '股民讨论次数',
  `IndustryCode` varchar(100) NOT NULL COMMENT '经传行业代码',
  `Website` varchar(200) NOT NULL COMMENT '公告网址',
  `Influence` bigint(20) DEFAULT NULL COMMENT '影响力',
  `IfShow` tinyint(4) NOT NULL DEFAULT 1 COMMENT '软件是否展示：0-不展示，1-展示',
  `CreateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `UpdateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `un1` (`SecuCode`,`EventCode`,`PubDate`),
  KEY `k1` (`SecuCode`,`EventCode`,`PubDate`,`PubDatetime`,`IfShow`,`UpdateTime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='股票公告事件追踪' ;



从公告事件明细表中获取基础数据:
CREATE TABLE `dc_ann_event_source_ann_detail` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `AnnID` bigint(20) NOT NULL COMMENT '公告主表ID',
  `PubTime` datetime NOT NULL COMMENT '发布时间（精确到秒）',
  `Title` varchar(500) DEFAULT NULL COMMENT '标题',
  `PDFLink` varchar(1000) DEFAULT NULL COMMENT 'PDF链接',
  `SecuCode` varchar(20) DEFAULT NULL COMMENT '股票代码',
  `EventCode` varchar(20) DEFAULT NULL COMMENT '事件代码',
  `EventName` varchar(1000) DEFAULT NULL COMMENT '事件名称',
  `IsValid` tinyint(4) NOT NULL DEFAULT 1 COMMENT '是否有效',
  `CreateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `UpdateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `un1` (`AnnID`,`SecuCode`,`EventCode`),
  KEY `k1` (`AnnID`,`PubTime`,`SecuCode`,`EventCode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='公告舆情事件明细--公告源' ;


# 新闻中间明细表
CREATE TABLE `dc_ann_event_source_news_detail` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `NewsID` bigint(20) NOT NULL COMMENT '新闻主表ID',
  `PubTime` datetime NOT NULL COMMENT '发布时间（精确到秒）',
  `Title` varchar(500) DEFAULT NULL COMMENT '标题',
  `Website` varchar(1000) DEFAULT NULL COMMENT '网址',
  `SecuCode` varchar(20) DEFAULT NULL COMMENT '股票代码',
  `EventCode` varchar(20) DEFAULT NULL COMMENT '事件代码',
  `EventName` varchar(1000) DEFAULT NULL COMMENT '事件名称',
  `Position` tinyint(4) NOT NULL COMMENT '提及位置：1-标题,2-内容',
  `IsValid` tinyint(4) NOT NULL DEFAULT 1 COMMENT '是否有效',
  `CreateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `UpdateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `un1` (`NewsID`,`SecuCode`,`EventCode`),
  KEY `k1` (`NewsID`,`PubTime`,`SecuCode`,`EventCode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='公告舆情事件明细-新闻源' ;

# 股吧中间明细表
CREATE TABLE `dc_ann_event_source_guba_detail` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `GubaID` bigint(20) NOT NULL COMMENT '股吧主表ID',
  `PubTime` datetime NOT NULL COMMENT '发布时间（精确到秒）',
  `Title` varchar(500) DEFAULT NULL COMMENT '标题',
  `Website` varchar(1000) DEFAULT NULL COMMENT '网址',
  `SecuCode` varchar(20) DEFAULT NULL COMMENT '股票代码',
  `EventCode` varchar(20) DEFAULT NULL COMMENT '事件代码',
  `EventName` varchar(1000) DEFAULT NULL COMMENT '事件名称',
  `Position` tinyint(4) NOT NULL COMMENT '提及位置：1-标题,2-内容',
  `IsValid` tinyint(4) NOT NULL DEFAULT 1 COMMENT '是否有效',
  `CreateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `UpdateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `un1` (`GubaID`,`SecuCode`,`EventCode`),
  KEY `k1` (`GubaID`,`PubTime`,`SecuCode`,`EventCode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='公告舆情事件明细-股吧源' ;


InnerCode - 由 SecuCode 可生成;
SecuCode - dc_ann_event_source_ann_detail 中的 SecuCode;
EventCode - dc_ann_event_source_ann_detail 中的 EventCode 关联 sf_const_announcement ;
PubDate -  由 PubDatetime 可生成;
PubDatetime - dc_ann_event_source_ann_detail 中的 PubTime;
NewsNum - 统计新闻发布时间在公告发布时间之后的所有关联篇数 select * from dc_ann_event_source_news_detail A where A.SecuCode = 'code' and A.EventCode = 'eventcode' and PubTime between {} amd {} ;
PostNum - 统计股吧发布时间在公告发布时间之后的所有关联贴数 同上
IndustryCode - 取主题猎手数据库 select A.code as IndustryCode, A.name as IndustryName, B.code as SecuCode, B.name as SecuAbbr
from block A, block_code B where B.code = 'SH600000' and A.type = 1 and A.id = B.bid ;
Website - dc_ann_event_source_ann_detail 中的 PDFLink;
Influence - 关联到的新闻在 dc_const_media_info 中对应的新闻源权重之和, 没有则赋值权重值为 1

"""


