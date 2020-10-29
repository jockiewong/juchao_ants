# 接股吧数据源 --> guba_base(敏仪) --> dc_ann_event_source_guba_detail

# guba_base 等敏仪灌入数据
import os
import sys

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from base_spider import SpiderBase


class GubaGenerator(SpiderBase):
    '''
    CREATE TABLE `guba_base` (
      `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
      `SecuCode` varchar(100) NOT NULL COMMENT '帖子所在的吧对应的股票交易代码(不带后缀与前缀，如600000)',
      `PubDatetime` datetime NOT NULL COMMENT '发布日期时间(精确到秒)',
      `Title` varchar(200) DEFAULT NULL COMMENT '标题',
      `Content` longtext DEFAULT NULL COMMENT '内容',
      `IfIrrigationPost` tinyint(1) NOT NULL COMMENT '是否灌水帖（默认为0。1-是，0-不是）',
      `Website` varchar(200) DEFAULT NULL COMMENT '网址',
      `DetailString` varchar(5000) DEFAULT NULL COMMENT '明细字符串(可用程序转化为dict格式)',
      `AuthorName` varchar(100) DEFAULT NULL COMMENT '作者用户名',
      `IfVerified` tinyint(1) DEFAULT NULL COMMENT '是否认证用户(1-是，0-不是)',
      `VerifiedLevel` varchar(100) DEFAULT NULL COMMENT '用户等级(有就写，没有就留空)',
      `AuthorType` tinyint(1) NOT NULL COMMENT '作者类别 1-股民，2-网站官方号',
      `OrgTableCode` int(10) NOT NULL COMMENT '原始来源网站编码',
      `OrgID` bigint(20) NOT NULL COMMENT '原始来源表主键id',
      `CMFTime` datetime DEFAULT NULL COMMENT '爬虫表中这条文本的写入时间',
      `CreateTime` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '入表时间',
      `UpdateTime` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
      PRIMARY KEY (`id`),
      UNIQUE KEY `un2` (`OrgTableCode`,`OrgID`),
      KEY `k1` (`SecuCode`,`PubDatetime`,`AuthorType`,`UpdateTime`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=810001 COMMENT='股吧主贴表';

    '''

    pass

