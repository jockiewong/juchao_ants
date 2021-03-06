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
  `IndustryCode` varchar(100) DEFATLT NULL COMMENT '经传行业代码',
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
  `MedName` varchar(100) DEFAULT NULL COMMENT '媒体名称',
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='公告舆情事件明细-新闻源';

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
NewsNum - 统计新闻发布时间在公告发布时间之后的所有关联篇数, 最多统计发布日之后的所有关联篇数，最多统计发布日(包括当日)之后的 5 个交易日之间的新闻，
超过 5 个交易日就不需要去更新这条记录了。
select * from dc_ann_event_source_news_detail A where A.SecuCode = 'code' and A.EventCode = 'eventcode' and PubTime between {} amd {} ;

PostNum - 统计股吧发布时间在公告发布时间之后的所有关联贴数 要求同上
IndustryCode - 取主题猎手数据库
select A.code as IndustryCode, A.name as IndustryName, B.code as SecuCode, B.name as SecuAbbr from block A, block_code B where B.code = 'SH600000' and A.type = 1 and A.id = B.bid ;
Website - dc_ann_event_source_ann_detail 中的 PDFLink;
Influence - 关联到的新闻在 dc_const_media_info 中对应的新闻源权重之和, 没有则赋值权重值为 1

"""
'''辅助用表: 
(1) 公告事件常量表: 
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


CREATE TABLE `dc_const_media_info` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `MedCode` varchar(100) NOT NULL COMMENT '媒体编码',
  `MedName` varchar(100) NOT NULL COMMENT '媒体名称',
  `InfluenceWeight` int(11) DEFAULT NULL COMMENT '影响力权重',
  `WebType1` varchar(100) DEFAULT NULL COMMENT '网站性质:L1-政府官方网站，L2-影响力较高的网站,L3-行业深度网站,L4-财经门户网站',
  `WebType2` varchar(100) DEFAULT NULL COMMENT '媒体类别',
  `Website` varchar(1000) DEFAULT NULL COMMENT '网站首页链接',
  `IfGetIn` tinyint(4) DEFAULT NULL COMMENT '爬虫是否已接入(1-已接入，0-未接入)',
  `BeginDate` datetime DEFAULT NULL COMMENT '爬虫开始接入日期',
  `EndDate` datetime DEFAULT NULL COMMENT '爬虫结束接入日期',
  `IsValid` tinyint(4) NOT NULL DEFAULT 1 COMMENT '是否有效',
  `CreateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `UpdateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `un1` (`MedCode`),
  UNIQUE KEY `un2` (`MedName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='中间表-媒体信息表' ; 

CREATE TABLE `block` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增的ID',
  `type` tinyint(4) NOT NULL COMMENT '板块类型1:行业, 2:地区, 3:指数, 4:主题, 5:盘口(主题和盘口都属于概念)',
  `code` varchar(32) NOT NULL COMMENT '板块代码',
  `name` varchar(255) NOT NULL COMMENT '板块名称',
  `status` tinyint(4) NOT NULL COMMENT '状态0:不可用, 1:可用',
  `deleted` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否需要被删除,0不删除,1删除, 如果为1,将在每天系统生成板块文件之前, 会删除这些数据',
  `create_at` int(11) NOT NULL COMMENT '创建时间',
  `update_at` int(11) NOT NULL COMMENT '更新时间',
  `update_user` int(11) NOT NULL COMMENT '更新人',
  `needhis` tinyint(4) NOT NULL DEFAULT '0',
  `segmode` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否是不定时调仓',
  `isprotected` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否是受保护的板块',
  `ispublic` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否是可以公开的板块',
  `isfund` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否是基金板块',
  `jyname` varchar(255) NOT NULL DEFAULT '' COMMENT '聚源概念名称',
  `jycode` varchar(64) NOT NULL DEFAULT '' COMMENT '聚源概念代码',
  `uptoday` tinyint(4) NOT NULL DEFAULT '0' COMMENT '今天发生过更新,1:是 0:否',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`) USING BTREE,
  KEY `codename` (`code`,`name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='统一板块代码' ; 

CREATE TABLE `block_code` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `type` tinyint(4) NOT NULL COMMENT '类型1:行业, 2:地区, 3:指数',
  `bid` int(11) NOT NULL COMMENT '所在板块的ID',
  `sid` int(11) NOT NULL COMMENT '股票代码ID',
  `code` varchar(32) NOT NULL COMMENT '代码',
  `name` varchar(255) NOT NULL COMMENT '名称',
  `status` tinyint(4) NOT NULL DEFAULT '1' COMMENT '状态0:不可用, 1:可用',
  `level` int(11) NOT NULL DEFAULT '0' COMMENT '级别,0:未处理, 1:非核心, 2:核心',
  `intop` int(11) NOT NULL DEFAULT '0' COMMENT '是否在前6的活跃股, 0:不是, 1：是',
  `deleted` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否需要被删除,0不删除,1删除, 如果为1,将在每天系统生成板块文件之前, 会删除这些数据',
  `create_at` int(11) NOT NULL COMMENT '创建时间',
  `update_at` int(11) NOT NULL COMMENT '更新时间',
  `update_user` int(11) NOT NULL COMMENT '更新人',
  PRIMARY KEY (`id`),
  UNIQUE KEY `bid_sid` (`bid`,`sid`),
  KEY `code` (`code`,`name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='板块股票关系' ; 
'''

import os
import sys
import datetime

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from configs import YQ_HOST, YQ_PORT, YQ_USER, YQ_PASSWD, YQ_DB, THE_HOST, THE_PORT, THE_USER, THE_PASSWD, THE_DB
from sql_base import Connection


class FinalAntDetail(object):
    def __init__(self,
                 start_time: datetime.datetime = None,
                 end_time: datetime.datetime = None,
                 ):
        self.source_table = 'dc_ann_event_source_ann_detail'
        self.target_table = 'sf_secu_announcement_detail'
        self.tool_table = "secumain"
        self.trading_table = 'tradingday'
        self.codes_map = {}
        self.industry_map = {}
        self.med_inf_map = {}

        self.start_time = start_time
        self.end_time = end_time
        self.trading_days = None
        self._yuqing_conn = Connection(
            host=YQ_HOST,
            port=YQ_PORT,
            user=YQ_USER,
            password=YQ_PASSWD,
            database=YQ_DB,
        )
        # 主题猎手数据库
        self._theme_conn = Connection(
            host=THE_HOST,
            port=THE_PORT,
            user=THE_USER,
            password=THE_PASSWD,
            database=THE_DB,
        )

    def get_inner_code_map(self):
        sql = '''select SecuCode, InnerCode from {} where SecuCode in (select distinct(SecuCode) from {}); '''.format(
            self.tool_table, self.source_table,
        )
        ret = self._yuqing_conn.query(sql)
        for r in ret:
            self.codes_map[r.get('SecuCode')] = r.get('InnerCode')

    def get_day(self, dt: datetime.datetime):
        return datetime.datetime(dt.year, dt.month, dt.day)

    def get_industry_code_map(self):
        sql = '''select A.code as IndustryCode, A.name as IndustryName, B.code as SecuCode, \
B.name as SecuAbbr from block A, block_code B where A.type = 1 and A.id = B.bid ;'''
        ret = self._theme_conn.query(sql)
        for r in ret:
            self.industry_map[r.get("SecuCode")] = r.get("IndustryCode")

    def get_all_trading_days(self, start_dt: datetime.datetime, end_dt:datetime.datetime):
        """
        获取起止时间之间的全部交易日并且排序
        :param start_dt:
        :param end_dt:
        :return:
        """
        sql = '''select Date from  {} where SecuMarket = 83 and IfTradingDay = 1 and Date between '{}' and '{}'; '''.format(
            self.trading_table, start_dt, end_dt
        )
        trading_days = self._yuqing_conn.query(sql)
        trading_days = sorted([trading_day.get("Date") for trading_day in trading_days])
        return trading_days

    def get_after_five_trading_days(self, dt: datetime.datetime):
        """当日（包括当日之后的）5 个交易日
        将一段时间内的全部交易日全部拿出来放在一个列表中排序
        取某一天的时间的索引（若不存在取之后最近的一个）然后顺次取之后第五个索引即可
        未击中时间范围时重新计算
        """
        while True:
            try:
                _index = self.trading_days.index(dt)
            except ValueError:
                dt += datetime.timedelta(days=1)
            else:
                break
        return self.trading_days[_index], self.trading_days[_index+4]

    def get_med_inf_map(self):
        sql = '''select MedName, InfluenceWeight from dc_const_media_info ; '''
        ret = self._yuqing_conn.query(sql)
        for r in ret:
            self.med_inf_map[r.get("MedName")] = int(r.get("InfluenceWeight"))

    def get_meds_scores(self, meds: list):
        """
        计算媒体得分 得分有 1 3 10 100
        无名媒体(None) 计 1 分
        :param meds:
        :return:
        """
        total_score = 0

        r_meds = []
        for med in meds:
            if med is None:
                total_score += 1
            else:
                r_meds.append(med)

        if len(r_meds) != 0:
            scores = [self.med_inf_map.get(r_med, 1) for r_med in r_meds]
            total_score += sum(scores)
        return total_score

    def get_news_num(self, secu_code: str, event_code: str, min_trading_day: datetime.datetime,
                     max_trading_day: datetime.datetime):
        """
        统计新闻发布时间在公告发布时间之后的所有关联篇数, 最多统计发布日之后的所有关联篇数，
        最多统计发布日(包括当日)之后的 5 个交易日之间的新闻,超过 5 个交易日就不需要去更新这条记录了.
        select * from dc_ann_event_source_news_detail A where A.SecuCode = '{}' and A.EventCode = '{}'
        and PubTime between {} amd {} ;
        """
        sql = '''select MedName from dc_ann_event_source_news_detail where SecuCode = '{}' \
and EventCode = '{}' and PubTime between '{}' and '{}' ;'''.format(
            secu_code, event_code, min_trading_day, max_trading_day)
        datas = self._yuqing_conn.query(sql)
        count = len(datas)
        total_scores = 0
        if count != 0:
            meds = [data.get("MedName") for data in datas]  # dict
            total_scores = self.get_meds_scores(meds)
        return count, total_scores

    def get_post_num(self, secu_code: str, event_code: str, min_trading_day: datetime.datetime,
                     max_trading_day: datetime.datetime):
        sql = '''select count(*) as count from dc_ann_event_source_guba_detail where SecuCode = '{}' \
and EventCode = '{}' and PubTime between '{}' and '{}' ;'''.format(
            secu_code, event_code, min_trading_day, max_trading_day)
        count = self._yuqing_conn.get(sql).get("count")
        return count

    def process_data(self, data: dict):
        secu_code = data.get("SecuCode")
        inner_code = self.codes_map.get(secu_code)
        event_code = data.get("EventCode")
        pub_time = data.get("PubTime")
        pub_date = self.get_day(pub_time)
        link = data.get("PDFLink")
        industry_code = self.industry_map.get(secu_code)
        min_trading_day, max_trading_day = self.get_after_five_trading_days(pub_date)
        item = {}
        item['SecuCode'] = secu_code
        item['InnerCode'] = inner_code
        item['EventCode'] = event_code
        item['PubDatetime'] = pub_time
        item['PubDate'] = pub_date
        item['Website'] = link
        item['IndustryCode'] = industry_code
        news_num, scores = self.get_news_num(secu_code, event_code, min_trading_day, max_trading_day)
        item['NewsNum'] = news_num
        item['Influence'] = scores
        item['PostNum'] = self.get_post_num(secu_code, event_code, min_trading_day, max_trading_day)
        return item

    def get_update_start(self):
        try:
            sql = '''select max(PubDatetime) as max_dt from {} ; '''.format(self.target_table)
            max_dt = self._yuqing_conn.get(sql).get("max_dt")
        except:
            max_dt = None
        return max_dt

    def get_update_end(self):
        return datetime.datetime.now()

    def daily_update(self):
        update_start = self.get_update_start()
        update_start = update_start - datetime.timedelta(days=7)
        update_end = self.get_update_end()
        print(update_start, update_end)

        self.get_inner_code_map()
        self.get_industry_code_map()
        self.get_med_inf_map()

        if not self.trading_days:
            self.trading_days = self.get_all_trading_days(update_start, update_end+datetime.timedelta(days=30))

        sql = '''select SecuCode, EventCode, PubTime, PDFLink from {} where PubTime between '{}' and '{}'; '''.format(
            self.source_table, update_start, update_end)
        datas = self._yuqing_conn.query(sql)
        for data in datas:
            item = self.process_data(data)
            print(item)
            self._yuqing_conn.table_insert(self.target_table, item)
