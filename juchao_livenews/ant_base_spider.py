sql = '''
CREATE TABLE `announcement_base` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `SecuCode` varchar(100) NOT NULL COMMENT '股票代码',
  `PDFLink` varchar(1000) DEFAULT NULL COMMENT '公告pdf地址',
  
  `PubDatetime1` datetime NOT NULL COMMENT '公告发布时间(巨潮公告速递栏目中的时间)',
  `InsertDatetime1` datetime NOT NULL COMMENT '爬虫入库时间(巨潮公告速递栏目)',
  `Title1` varchar(1000) NOT NULL COMMENT '巨潮公告速递栏目中的标题',
  
  `PubDatetime2` datetime DEFAULT NULL COMMENT '公告发布时间(巨潮快讯栏目中的时间)',
  `InsertDatetime2` datetime DEFAULT NULL COMMENT '爬虫入库时间(巨潮快递栏目)',
  `Title2` varchar(1000) DEFAULT NULL COMMENT '巨潮快讯栏目中的标题（没有则留空）',
  
  `CreateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `UpdateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `un1` (`PDFLink`),
  KEY `k1` (`SecuCode`,`PubDatetime1`,`PubDatetime2`,`UpdateTime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='公告基础表';

'''