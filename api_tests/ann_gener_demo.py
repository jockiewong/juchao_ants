import datetime
import json
import multiprocessing
import os
import sys
import threading
import time
from functools import wraps

import requests

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from base_spider import SpiderBase


def timing(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        r = func(*args, **kwargs)
        end = time.perf_counter()
        print('[' + func.__name__ + ']used:' + str(end - start))
        return r
    return wrapper


@timing
def api_test():
    Threads = []
    THREAD_NUM = 200

    def work_test():
        data = {'texttype': 'news',
                'title': "我来call一次接口耶",
                'content': "我来call一次接口耶",
                'prolist': ['event_ann']
                }
        data_json = json.dumps(data)
        resp = requests.post('http://139.159.245.37:9009/jznlpsv/v2/query/', data_json)
        if resp and resp.status_code == 200:
            print(resp.text)

    for i in range(THREAD_NUM):
        t = threading.Thread(target=work_test, name="T" + str(i))
        t.setDaemon(True)
        Threads.append(t)
    for t in Threads:
        t.start()
    for t in Threads:
        t.join()
    '''
    [api_test]used:0.8137136180000001 # 1 
    [api_test]used:0.724188025        # 5 
    [api_test]used:0.8458107020000001  # 10 
    [api_test]used:1.383296724      # 20 
    [api_test]used:2.701941949     # 50 
    [api_test]used:3.644817121     # 100
    [api_test]used:5.901716985     # 200
    ... 

    
    '''


class AnnGenerator(SpiderBase):
    """测试公告模型接口用"""
    def __init__(self, start_time: datetime.datetime, end_time: datetime.datetime):
        super(AnnGenerator, self).__init__()
        self.api = "http://139.159.245.37:9009/jznlpsv/v2/query/"
        self.target_table_name = 'dc_ann_event_source_ann_detail'
        self.target_fields = ['AnnID', 'PubTime', 'Title', 'PDFLink', 'SecuCode', 'EventCode', 'EventName']
        self.batch_num = 100
        self.start_time = start_time
        self.end_time = end_time

    def launch(self):
        datas = self.get_origin_datas()
        print("req datas: ", len(datas))
        items = self.post_api(datas)
        print("post resp: ", len(items))
        self._batch_save(self.tonglian_client, items, self.target_table_name, self.target_fields)

    def get_origin_datas(self):
        self._tonglian_init()
        sql = '''select * from announcement_base where UpdateTime > '{}' and UpdateTime < '{}'; '''.format(self.start_time, self.end_time)
        print("sql is: ", sql)
        datas = self.tonglian_client.select_all(sql)
        return datas

    @timing
    def post_task(self, req_data, data, title):
        data_json = json.dumps(req_data).encode('utf8')
        resp = requests.post(self.api, data_json)
        return_data = json.loads(resp.text)
        if return_data.get("event_ann"):
            return_data = return_data.get("event_ann")[0]
            item = {}
            item['AnnID'] = data.get("id")
            item['PubTime'] = data.get("PubDatetime1")
            item['Title'] = title
            item['PDFLink'] = data.get("PDFLink")
            item['SecuCode'] = data.get('SecuCode')
            item['EventCode'] = return_data.get("event_code")
            item['EventName'] = return_data.get("event_name")
            return item

    # @timing
    def post_api(self, datas):
        # TODO post 接口部分优化
        params = []
        for data in datas:
            title = data.get("Title2")
            if not title:
                title = data.get('SecuAbbr') + data.get("Title1")
            req_data = {
                'texttype': 'ann',
                'title': title,
                'content': title,
                'prolist': ['event_ann'],
            }
            params.append((req_data, data, title))
        items = []

        # TODO 测试接口合适并发数
        for param in params:
            item = self.post_task(*param)
            if item:
                items.append(item)
        return items

    def _ret_table(self):
        sql = '''
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='公告舆情事件明细--公告源';
        '''


# def process_task(args):
#     start, end = args[0], args[1]
#     print("start is {} and end is {}".format(start, end))
#     AnnGenerator(start=start, end=end).launch()
#
#
# def dispath(max_number):
#     for start in range(2, max_number // 100 + 1):
#         yield start * 100 + 1, start*100 + 100
#
#
# def api_schedule():
#     mul_count = multiprocessing.cpu_count()
#     print("mul count: ", mul_count)
#
#     with multiprocessing.Pool(mul_count) as workers:
#         workers.map(process_task, dispath(500 * 10**4))


if __name__ == '__main__':
    # _end_time = datetime.datetime.now()
    # _start_time = _end_time - datetime.timedelta(days=1)
    # AnnGenerator(_start_time, _end_time).launch()

    # g_ = dispath(10000)
    # for one in g_:
    #     print(one)

    # api_schedule()


    api_test()

    pass


'''
(0, 100) --> ok 


'''