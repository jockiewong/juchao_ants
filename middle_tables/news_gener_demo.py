# 接新闻数据源 -->  news_base_tonglian(良哥) --> dc_ann_event_source_news_detail
# 新闻先直接接通联库的数据
import datetime
import json
import logging
import os
import sys
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor

import requests

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

log_file = os.path.join(cur_path, 'news.log')
logging.basicConfig(level=logging.INFO, filename=log_file, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from base_spider import SpiderBase


class NewsGenerator(SpiderBase):
    # vnews_content_v1  标题
    # vnews_body_v1  内容
    # 'NewsID', 'PubTime', 'Title', 'Website', 'SecuCode', 'EventCode', 'EventName', 'Position'

    '''
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

    CREATE TABLE `vnews_content_v1` (
      `NEWS_ID` bigint(20) NOT NULL DEFAULT '0',
      `INSERT_TIME` datetime DEFAULT NULL,
      `UPDATE_TIME` datetime DEFAULT NULL,
      `NEWS_ORIGIN_SOURCE` varchar(50) DEFAULT NULL,
      `NEWS_AUTHOR` varchar(500) DEFAULT NULL,
      `NEWS_URL` varchar(500) DEFAULT NULL,
      `NEWS_TITLE` varchar(300) DEFAULT NULL,
      `GROUP_ID` bigint(20) DEFAULT NULL,
      `NEWS_PUBLISH_SITE` varchar(50) DEFAULT NULL,
      `NEWS_PUBLISH_TIME` datetime DEFAULT NULL,
      `EFFECTIVE_TIME` datetime DEFAULT NULL,
      PRIMARY KEY (`NEWS_ID`) USING BTREE,
      KEY `public_time` (`NEWS_PUBLISH_TIME`),
      KEY `update_time` (`UPDATE_TIME`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8  ;

     CREATE TABLE `vnews_body_v1` (
      `NEWS_ID` bigint(20) NOT NULL DEFAULT '0',
      `NEWS_BODY` longtext,
      `INSERT_TIME` datetime DEFAULT NULL,
      `UPDATE_TIME` datetime DEFAULT NULL,
      PRIMARY KEY (`NEWS_ID`) USING BTREE,
      KEY `update_time` (`UPDATE_TIME`),
      KEY `insert_time` (`INSERT_TIME`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;
    '''

    def __init__(self, start_time, end_time):
        super(NewsGenerator, self).__init__()
        self.content_table_name = 'vnews_content_v1'
        self.body_table_name = 'vnews_body_v1'
        self.batch_num = 10000
        self.target_table_name = 'dc_ann_event_source_news_detail'
        self.target_fields = ['NewsID', 'PubTime', 'Title', 'Website', 'SecuCode', 'EventCode',
                              'EventName', 'Position', 'MedName']
        self.start_time = start_time
        self.end_time = end_time

    def post_api(self, data: dict):
        req_data = {'texttype': 'news',
                    'title': data.get("NEWS_TITLE"),
                    'content': data.get("NEWS_BODY"),
                    'prolist': ['event_ann'],
                    }
        data_json = json.dumps(req_data)
        try:
            resp = requests.post('http://139.159.245.37:9009/jznlpsv/v2/query/', data_json, timeout=10)
            # resp = requests.post('http://0.0.0.0:9009/jznlpsv/v2/query/', data_json, timeout=10)
        except Exception as e:
            print(e)
            resp = None
            logger.warning(f'{data.get("NEWS_ID")}\n')
            print(f'{data.get("NEWS_ID")}\n')
            # with open("news_err.log", 'a') as f:
            #     f.write(f'{data.get("NEWS_ID")}\n')

        if resp and resp.status_code == 200:
            body = json.loads(resp.text)
            if body.get("event_ann"):
                ret = body.get("event_ann")[0]
                item = {}
                item['NewsID'] = data.get("NEWS_ID")
                item['MedName'] = data.get("NEWS_PUBLISH_SITE")
                item['PubTime'] = data.get('NEWS_PUBLISH_TIME')
                item['Title'] = data.get("NEWS_TITLE")
                item['Website'] = data.get("NEWS_URL")
                item['SecuCode'] = ret.get("secucode")
                item['EventCode'] = ret.get("event_code")
                item['Position'] = 2 if ret.get("position") == "content" else 1   # 提及位置：1-标题,2-内容
                return item
        else:
            return None

    def select_max_title_id(self):
        # 以标题中的新闻id为准
        self._tonglian_init()
        sql = '''select min(NEWS_ID) as min_id, max(NEWS_ID) as max_id from {} where NEWS_PUBLISH_TIME between '{}' and '{}'; '''.format(
            self.content_table_name, self.start_time, self.end_time)
        data = self.tonglian_client.select_one(sql)
        max_id, min_id = data.get("max_id"), data.get("min_id")
        return max_id, min_id

    def launch2(self):
        self._tonglian_init()
        self._yuqing_init()

        dt = self.start_time
        while dt <= self.end_time:
            end_dt = dt + datetime.timedelta(days=1)
            sql = '''select T.NEWS_ID, T.NEWS_URL, T.NEWS_ORIGIN_SOURCE, T.NEWS_PUBLISH_TIME, T.NEWS_TITLE, T.NEWS_PUBLISH_SITE, B.NEWS_BODY \
from vnews_content_v1 T, vnews_body_v1 B \
where T.NEWS_PUBLISH_TIME between '{}' and '{}' \
and T.NEWS_ID = B.NEWS_ID; '''.format(dt, end_dt)
            print(sql)
            datas = self.tonglian_client.select_all(sql)
            print("当前数据量是: ", len(datas))
            items = []
            with ThreadPoolExecutor(max_workers=10) as t:
                res = [t.submit(self.post_api, data) for data in datas]
            for future in as_completed(res):
                item = future.result()
                if item:
                    items.append(item)
            print(len(items))
            self._batch_save(self.yuqing_client, items, self.target_table_name, self.target_fields)
            self.yuqing_client.end()
            dt = end_dt

    def launch(self):
        self._tonglian_init()
        self._yuqing_init()

        max_id, min_id = self.select_max_title_id()
        print("news_id 的范围是: ", min_id, max_id)
        for i in range(min_id // self.batch_num, max_id // self.batch_num + 1):
            news_id_start = self.batch_num * i
            news_id_end = self.batch_num * (i+1)
            print("当前范围是: ", news_id_start, news_id_end)
            sql = '''select T.NEWS_ID, T.NEWS_PUBLISH_TIME, T.NEWS_TITLE, T.NEWS_PUBLISH_SITE, B.NEWS_BODY \
from vnews_content_v1 T, vnews_body_v1 B \
where T.NEWS_ID >= {} and T.NEWS_ID <= {} \
and B.NEWS_ID >= {} and B.NEWS_ID <= {}  \
and T.NEWS_ID = B.NEWS_ID \
and T.NEWS_PUBLISH_TIME between '{}' and '{}'; '''.format(news_id_start, news_id_end, news_id_start, news_id_end, self.start_time, self.end_time)
            print("sql: ", sql)
            datas = self.tonglian_client.select_all(sql)
            print("当前数据量是: ", len(datas))

            items = []
            with ThreadPoolExecutor(max_workers=10) as t:
                res = [t.submit(self.post_api, data) for data in datas]
            for future in as_completed(res):
                item = future.result()
                if item:
                    # print(">>> ", item)
                    items.append(item)

            print(len(items))
            self._batch_save(self.yuqing_client, items, self.target_table_name, self.target_fields)
            self.yuqing_client.end()


if __name__ == '__main__':    # 2019-10-01 - 2020-10-01 ; 2020-10-01 - 2020-11-06
    _start = datetime.datetime(2020, 10, 1)
    _end = datetime.datetime(2020, 11, 6)
    # NewsGenerator(_start, _end).launch()
    NewsGenerator(_start, _end).launch2()
