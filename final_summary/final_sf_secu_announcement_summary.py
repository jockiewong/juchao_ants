'''公告重大事件汇总表
CREATE TABLE `sf_secu_announcement_summary` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `InnerCode` int(10) DEFAULT NULL COMMENT '股票内部编码',
  `SecuCode` varchar(100) NOT NULL COMMENT '股票代码',
  `TradeDate` datetime NOT NULL COMMENT '日期',
  `Sentiment` tinyint(4) NOT NULL COMMENT '情感倾向标签(重大事件)(显示颜色)',
  `EventCode` varchar(100) NOT NULL COMMENT '公告事件类型（显示标签名称）',
  `AnnID` bigint(20) NOT NULL COMMENT '公告基础表中的ID字段',
  `AnnTitle` varchar(1000) DEFAULT NULL COMMENT '公告标题',
  `Website` varchar(200) DEFAULT NULL COMMENT '网址',
  `IfShow` tinyint(4) NOT NULL DEFAULT 1 COMMENT '是否软件展示(1-展示，0-不展示)',
  `CreateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `UpdateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `un1` (`SecuCode`,`TradeDate`,`EventCode`),
  KEY `k1` (`SecuCode`,`TradeDate`,`Sentiment`,`EventCode`,`IfShow`,`UpdateTime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='股票-公告重大事件汇总表';


SecuCode, InnerCode : 从 dc_ann_event_source_ann_detail 中的 SecuCode 生成;
TradeDate: 从 dc_ann_event_source_ann_detail 中的 PubTime 可生成;
生成规则: 如果公告的发布时间为交易日，则使用这一天。
如果不是, 则使用之前最近的一个交易日。
用到的表 tradingday

Sentiment: 用 dc_ann_event_source_ann_detail 中的 EventCode 与 sf_const_announcement 关联取其中的 Sentiment ;
EventCode: dc_ann_event_source_ann_detail 中的 EventCode;
AnnID: dc_ann_event_source_ann_detail 中的 AnnID ;
AnnTitle : dc_ann_event_source_ann_detail 中的 Title  ;
Website: dc_ann_event_source_ann_detail 中的 PDFLink ;
'''

import datetime
import logging
import os
import sys
import time

import schedule

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

log_file = os.path.join(cur_path, 'final2.log')
logging.basicConfig(level=logging.INFO, filename=log_file, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from base_spider import SpiderBase


class FinalAntSummary(SpiderBase):
    def __init__(self, start_time: datetime.datetime, end_time: datetime.datetime):
        super(FinalAntSummary, self).__init__()
        self.source_table = 'dc_ann_event_source_ann_detail'
        self.target_table = 'sf_secu_announcement_summary'
        self.target_fields = ['InnerCode', 'SecuCode', 'TradeDate', 'Sentiment', 'EventCode', 'AnnID', 'AnnTitle', 'Website']
        self.tool_table = "secumain"
        self.trading_table = 'tradingday'
        self.const_table = 'sf_const_announcement'

        self.start_time = start_time
        self.end_time = end_time
        self.codes_map = {}
        self.sent_map = {}

    def get_inner_code_map(self):
        self._yuqing_init()
        sql = '''select SecuCode, InnerCode from {} where SecuCode in (select distinct(SecuCode) from {}); '''.format(
            self.tool_table, self.source_table,
        )
        ret = self.yuqing_client.select_all(sql)
        for r in ret:
            self.codes_map[r.get('SecuCode')] = r.get('InnerCode')

    def get_sentiment_map(self):
        self._yuqing_init()
        sql = '''select EventCode, Sentiment from {} ; '''.format(self.const_table)
        ret = self.yuqing_client.select_all(sql)
        for r in ret:
            self.sent_map[r.get('EventCode')] = r.get("Sentiment")

    def get_nearest_trading_day(self, day: datetime.datetime):
        """获取距离当前时间最近的向前一个交易日 包括当前的日期"""
        self._yuqing_init()
        while True:
            sql = '''select IfTradingDay from {} where Date = '{}' and SecuMarket = 83 ; '''.format(self.trading_table, day)
            is_trading_day = self.yuqing_client.select_one(sql).get("IfTradingDay")
            if is_trading_day == 1:
                return day
            day -= datetime.timedelta(days=1)

    def get_update_endtime(self):
        self._yuqing_init()
        sql = '''select max(PubTime) as max_pub from {};  '''.format(self.source_table)
        try:
            max_pub = self.yuqing_client.select_one(sql).get("max_pub")
        except:
            max_pub = None
        return max_pub

    def get_update_starttime(self):
        self._yuqing_init()
        sql = '''select max(TradeDate) as max_trd from {}; '''.format(self.target_table)
        try:
            max_trd = self.yuqing_client.select_one(sql).get("max_trd")
        except:
            max_trd = None
        return max_trd

    def daily_update(self):
        update_end = self.get_update_endtime()
        update_start = self.get_update_starttime()
        print(update_start, update_end)

        self.get_inner_code_map()
        self.get_sentiment_map()

        sql = '''select AnnID, SecuCode, PubTime, EventCode, Title, PDFLink from {} where PubTime  between '{}' and '{}'; '''.format(
            self.source_table, update_start, update_end)
        print(sql)
        self._yuqing_init()
        datas = self.yuqing_client.select_all(sql)
        items = []
        for data in datas:
            ann_id = data.get("AnnID")
            pub_time = data.get("PubTime")
            event_code = data.get("EventCode")
            title = data.get("Title")
            link = data.get("PDFLink")
            secu_code = data.get("SecuCode")

            inner_code = self.codes_map.get(secu_code)
            pub_day = datetime.datetime(pub_time.year, pub_time.month, pub_time.day)
            trade_day = self.get_nearest_trading_day(pub_day)
            sentiment = self.sent_map.get(event_code)
            item = {}
            item['SecuCode'] = secu_code
            item['InnerCode'] = inner_code
            item['TradeDate'] = trade_day
            item['Sentiment'] = sentiment
            item['EventCode'] = event_code
            item['AnnID'] = ann_id
            item['AnnTitle'] = title
            item['Website'] = link
            items.append(item)
        print(len(items))
        print(">>>>>> ", self._batch_save(self.yuqing_client, items, self.target_table, self.target_fields))
        self.yuqing_client.end()

    def launch(self):
        self.get_inner_code_map()
        self.get_sentiment_map()

        sql = '''select AnnID, SecuCode, PubTime, EventCode, Title, PDFLink from {} where PubTime  between '{}' and '{}'; '''.format(
            self.source_table, self.start_time, self.end_time)
        print(sql)
        self._yuqing_init()
        datas = self.yuqing_client.select_all(sql)
        items = []
        for data in datas:
            ann_id = data.get("AnnID")
            pub_time = data.get("PubTime")
            event_code = data.get("EventCode")
            title = data.get("Title")
            link = data.get("PDFLink")
            secu_code = data.get("SecuCode")

            inner_code = self.codes_map.get(secu_code)
            pub_day = datetime.datetime(pub_time.year, pub_time.month, pub_time.day)
            trade_day = self.get_nearest_trading_day(pub_day)
            sentiment = self.sent_map.get(event_code)
            item = {}
            item['SecuCode'] = secu_code
            item['InnerCode'] = inner_code
            item['TradeDate'] = trade_day
            item['Sentiment'] = sentiment
            item['EventCode'] = event_code
            item['AnnID'] = ann_id
            item['AnnTitle'] = title
            item['Website'] = link
            items.append(item)

        print(len(items))
        print(">>>>>> ", self._batch_save(self.yuqing_client, items, self.target_table, self.target_fields))
        self.yuqing_client.end()


if __name__ == '__main__':
    # history
    # start_dt = datetime.datetime(2001, 5, 8)
    # end_dt = datetime.datetime(2020, 11, 12)
    # dt = start_dt
    # while dt <= end_dt:
    #     dt_next = dt + datetime.timedelta(days=1)
    #     FinalAntSummary(dt, dt_next).launch()
    #     dt = dt_next

    # update
    def task():
        FinalAntSummary(None, None).daily_update()

    task()
    schedule.every(10).minutes.do(task)

    while True:
        schedule.run_pending()
        print(schedule.jobs)
        time.sleep(20)
