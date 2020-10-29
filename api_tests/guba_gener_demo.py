# 接股吧数据源 --> guba_base(敏仪) --> dc_ann_event_source_guba_detail

# guba_base 等敏仪灌入数据

import datetime
import json
import os
import sys

import requests

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
    '''

    def __init__(self):
        super(GubaGenerator, self).__init__()
        self.source_table = 'guba_base'
        self.target_table = 'dc_ann_event_source_guba_detail'
        self.target_fields = ['GubaID', 'PubTime', 'Title', 'Website', 'SecuCode', 'EventCode',
                              'EventName', 'Position']
        self.batch_num = 10000

    # def get_codes(self):
    #     '''
    #     每天大概是 15w 条
    #     codes 有 3714 个
    #     每个 code 每天大概有 40 个
    #     单批次 10000 个 code 每 250 个一组？ T.T
    #
    #     select * from (select id,xxx from table_a where time…..) order by id limit 0,10000
    #
    #     '''
    #     self._yuqing_init()
    #     sql = '''select distinct(SecuCode) from {} ;'''.format(self.source_table)
    #     codes = self.yuqing_client.select_all(sql)
    #     codes = [one.get("SecuCode") for one in codes]
    #     return codes

    def post_api(self, data: dict):
        req_data = {
            'texttype': 'tieba',
            'title': data.get("Title"),
            'content': data.get("Content"),
            'prolist': ['event_ann'],
        }

        data_json = json.dumps(req_data)
        try:
            resp = requests.post('http://139.159.245.37:9009/jznlpsv/v2/query/', data_json, timeout=10)
        except Exception as e:
            print(e)
            resp = None
            with open("news_err.log", 'a') as f:
                f.write(f'{data.get("NEWS_ID")}\n')

        if resp and resp.status_code == 200:
            body = json.loads(resp.text)
            if body.get("event_ann"):
                resp_data = body.get('event_ann')[0]
                item = {
                    'GubaID': data.get("OrgID"),
                    'PubTime': data.get("PubDatetime"),
                    'Title': data.get("Title"),
                    'Website': data.get('Website'),
                    'SecuCode': data.get("SecuCode"),
                    'EventCode': resp_data.get("event_code"),
                    'EventName': resp_data.get("event_name"),
                    'Position': 2 if req_data.get('position') == 'content' else 1
                }
                return item

    def launch(self):
        self._yuqing_init()
        end_time = datetime.datetime(2020, 10, 27)
        # start_time = end_time - datetime.timedelta(days=185)
        start_time = end_time - datetime.timedelta(days=2)

        dt = start_time
        while dt <= end_time:
            dt_next = dt + datetime.timedelta(days=1)

            while True:
                limit_start = 0
                sql = '''select * from {} where PubDatetime >= '{}' and PubDatetime <= '{}' order by id limit {}, {};'''.format(
                    self.source_table, dt, dt_next, limit_start*self.batch_num, self.batch_num,
                )
                datas = self.yuqing_client.select_all(sql)
                items = []
                for data in datas:
                    item = self.post_api(data)
                    if item:
                        print(item)
                        items.append(item)
                print(len(items))
                self._batch_save(self.yuqing_client, items, self.target_table, self.target_fields)
                if len(datas) == 0:
                    break
                limit_start += 1
            dt = dt_next


if __name__ == '__main__':
    GubaGenerator().launch()
