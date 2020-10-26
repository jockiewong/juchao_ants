import datetime
import json
import multiprocessing
import os
import sys
import threading
import time
import timeit
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
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


# @timing
def api_test(thread_num):
    def work_test():
        data = {'texttype': 'news',
                'title': "我来call一次接口耶",
                'content': "我来call一次接口耶",
                'prolist': ['event_ann']
                }
        data_json = json.dumps(data)
        try:
            resp = requests.post('http://139.159.245.37:9009/jznlpsv/v2/query/', data_json)
        except Exception as e:
            print(e)
            resp = None
        if resp and resp.status_code == 200:
            # print(resp.text)
            pass

    _threads = []
    for i in range(thread_num):
        t = threading.Thread(target=work_test, name="T" + str(i))
        t.setDaemon(True)
        _threads.append(t)
    for t in _threads:
        t.start()
    for t in _threads:
        t.join()


if __name__ == '__main__':
    # print(timeit.timeit('api_test(1)', 'from __main__ import api_test',  number=10))      # 0.480385191
    # print(timeit.timeit('api_test(10)', 'from __main__ import api_test',  number=10))   # 0.597345931/10
    # print(timeit.timeit('api_test(100)', 'from __main__ import api_test',  number=10))  # 4.430669795/100
    # print(timeit.timeit('api_test(1000)', 'from __main__ import api_test',  number=10)) # 42.872432945999996/100
    # TODO 大概在 10

    # sys.exit(0)

    pass


class AnnGenerator(SpiderBase):
    """测试公告模型接口用"""
    def __init__(self,
                 start_time: datetime.datetime = None,
                 end_time: datetime.datetime = None,
                 start_id: int = None,
                 end_id: int = None,
                 ):
        super(AnnGenerator, self).__init__()
        self.api = "http://139.159.245.37:9009/jznlpsv/v2/query/"
        self.target_table_name = 'dc_ann_event_source_ann_detail'
        self.target_fields = ['AnnID', 'PubTime', 'Title', 'PDFLink', 'SecuCode', 'EventCode', 'EventName']
        self.batch_num = 100
        self.start_time = start_time
        self.end_time = end_time
        self.start_id = start_id
        self.end_id = end_id

    def launch(self):
        datas = self.get_origin_datas()
        print("req datas: ", len(datas))
        items = self.post_api(datas)
        print("post resp: ", len(items))
        self._batch_save(self.tonglian_client, items, self.target_table_name, self.target_fields)

    def get_origin_datas(self):
        self._tonglian_init()
        if self.start_time:
            # sql = '''select * from announcement_base where UpdateTime >= '{}' and UpdateTime <= '{}'; '''.format(self.start_time, self.end_time)
            sql = '''select * from announcement_base where PubDatetime1 >= '{}' and PubDatetime1 <= '{}'; '''.format(self.start_time, self.end_time)
        elif self.start_id:
            sql = '''select * from announcement_base where id > '{}' and id < '{}'; '''.format(self.start_id, self.end_id)
        else:
            raise ValueError
        print("sql is: ", sql)
        datas = self.tonglian_client.select_all(sql)
        return datas

    def post_task(self, req_data, data, title):
        try:
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
        except:
            # TODO  use log
            with open("error.log", "a") as f:
                f.write("请求{}失败".format(data.get("id")))
            return None

    def post_api(self, datas):
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

        with ThreadPoolExecutor(max_workers=10) as t:
            res = [t.submit(self.post_task, *param) for param in params]
        for future in as_completed(res):
            item = future.result()
            if item:
                items.append(item)

        # for param in params:
        #     try:
        #         item = self.post_task(*param)
        #     except:
        #         item = None
        #     if item:
        #         items.append(item)

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


def process_task(args):
    start, end = args[0], args[1]
    AnnGenerator(start_id=start, end_id=end).launch()


def dispath_id(max_number, start=None):
    for start in range(start // 100, max_number // 100 + 1):
        yield start * 100 + 1, start*100 + 100


@timing
def ip_schedule():
    mul_count = multiprocessing.cpu_count()
    print("mul count: ", mul_count)

    with multiprocessing.Pool(mul_count) as workers:
        workers.map(process_task, dispath_id(110*10**4, start=100*10**4))


@timing
def time_schedule():
    # 最近半年的
    _interval = 10
    _end_time = datetime.datetime.now()
    _start_time = _end_time - datetime.timedelta(days=365)

    _dt = _end_time
    while _dt > _start_time:
        AnnGenerator(start_time=_dt - datetime.timedelta(days=_interval), end_time=_dt).launch()
        _dt = _dt - datetime.timedelta(days=_interval)


if __name__ == '__main__':
    time_schedule()

    # ip_schedule()

    # api_test()

    pass
