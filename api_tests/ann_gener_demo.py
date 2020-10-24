import json
import multiprocessing

import requests

from base_spider import SpiderBase


class AnnGenerator(SpiderBase):
    """测试公告模型接口用"""
    def __init__(self):
        super(AnnGenerator, self).__init__()
        self.api = "http://139.159.245.37:9009/jznlpsv/v2/query/"
        self.target_table_name = 'dc_ann_event_source_ann_detail'
        self.target_fields = ['AnnID', 'PubTime', 'Title', 'PDFLink', 'SecuCode', 'EventCode', 'EventName']
        self.batch_num = 100

    def start(self):
        start = 100
        while True:
            datas = self.get_origin_datas(start)
            print("start: ", start, "len(datas): ", len(datas))
            if len(datas) == 0:
                break
            items = self.post_api(datas)
            self._batch_save(self.tonglian_client, items, self.target_table_name, self.target_fields)
            start += 1

    def get_origin_datas(self, start):
        self._tonglian_init()
        sql = '''select * from announcement_base limit {}, {}; '''.format(
            start*self.batch_num, self.batch_num)
        datas = self.tonglian_client.select_all(sql)
        return datas

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
        print(params)
        print(len(params))
        items = []

        for param in params:
            item = self.post_task(*param)
            if item:
                items.append(item)

        # mul_count = multiprocessing.cpu_count()
        # print("mul count: ", mul_count)
        # with multiprocessing.Pool(mul_count) as workers:
        #     item = workers.imap_unordered(self.post_task, params)
        #     if item:
        #         items.append(item)

        print("post resp: ", len(items))
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


if __name__ == '__main__':
    AnnGenerator().start()
