'''
CREATE TABLE `sf_const_announcement` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `EventMainTypeCode` varchar(20) NOT NULL COMMENT '事件所属的大类代码',
  `EventMainTypeName` varchar(50) NOT NULL COMMENT '事件所属的大类名称',
  `EventCode` varchar(50) NOT NULL COMMENT '事件代码',
  `EventName` varchar(100) NOT NULL COMMENT '事件名称',
  `EventOneWordLabel` varchar(50) DEFAULT NULL COMMENT '事件类型一字标签',
  `Sentiment` tinyint(4) NOT NULL COMMENT '情感倾向(1-正面，-1-负面，0-中性)',
  `Level` int(4) NOT NULL COMMENT '舆情级别：0为中性，负数越小，影响越利空；正数越大，影响越利多',
  `EventDayChgPerc` decimal(10,4) NOT NULL COMMENT '公告发布当日的涨跌幅',
  `EventDayWinRatio` decimal(10,4) NOT NULL COMMENT '公告发布当日的胜率',
  `NextDayWinRatio` decimal(10,4) NOT NULL COMMENT '次日胜率',
  `NextDayChgPerc` decimal(10,2) NOT NULL COMMENT '次日涨幅',
  `ThreeDayChgPerc` decimal(10,2) NOT NULL COMMENT '3日涨幅',
  `FiveDayChgPerc` decimal(10,2) NOT NULL COMMENT '5日涨幅',
  `Desc` varchar(1000) DEFAULT NULL COMMENT '事件描述',
  `IfShow` tinyint(4) NOT NULL DEFAULT 1 COMMENT '软件是否展示：0-不展示，1-展示',
  `FirstLevelShowRank` int(10) DEFAULT NULL COMMENT '公告智选前端展示排序-一级事件（对应EventMainTypeCode）（一个一级事件下面对应的多个二级事件每条数据需要保证这个字段一致）',
  `SecondLevelShowRank` int(10) DEFAULT NULL COMMENT '公告智选前端展示排序-二级事件（对应EventCode）',
  `CreateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `UpdateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `u1` (`EventName`),
  UNIQUE KEY `u2` (`EventCode`),
  UNIQUE KEY `u3` (`EventMainTypeCode`,`EventCode`,`SecondLevelShowRank`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='常量表-公告事件' ;

需要的字段:
EventMainTypeCode: 事件所属大类代码 : 后台人工录入 待后台接口完善后调用接口
EventMainTypeName: 事件所属大类名称:  后台人工录入 待后台接口完善后调用接口
EventCode 事件代码: 后台人工录入 待后台接口完善后调用接口
EventName 事件名称: 后台人工录入 待后台接口完善后调用接口
EventOneWordLabel: 事件类型--字标签: 后台管理
Sentiment: 情感倾向(1-正面，-1-负面，0-中性): 后台管理
Level: 舆情级别: 后台管理，0 为中性，负数越小，影响越利空； 整数越大，影响越利多
EventDayChgPerc :公告发布当日的涨跌幅: 近一年同类型的公告统计, 交易日收盘更新
EventDayWinRatio: 公告发布当日的胜率: 近一年同类型的公告统计, 交易日收盘更新
NextDayWinRatio: 次日胜率: 近一年同类型的公告统计, 交易日收盘更新
NextDayChgPerc: 次日平均涨幅: 近一年同类型的公告统计, 交易日收盘更新
ThreeDayChgPerc: 3日平均涨幅: 近一年同类型的公告统计, 交易日收盘更新
FiveDayChgPerc: 5日平均涨幅: 近一年同类型的公告统计, 交易日收盘更新
Desc: 事件描述: 后台管理
IfShow: 软件是否展示：0-不展示，1-展示: 后台管理
FirstLevelShowRank: 公告智选前端展示排序-一级事件（对应EventMainTypeCode）（一个一级事件下面对应的多个二级事件每条数据需要保证这个字段一致）: 后台管理
SecondLevelShowRank: 公告智选前端展示排序-二级事件（对应EventCode）: 后台管理
CreateTime: 创建时间
UpdateTime: 更新时间

生成逻辑:

'''

