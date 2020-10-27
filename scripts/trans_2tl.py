import datetime
import os
import sys
import time

import schedule

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from base_spider import SpiderBase


class MergeBase(SpiderBase):
    def __init__(self):
        super(MergeBase, self).__init__()
        self.merge_table_name = 'announcement_base'
        self.batch_number = 1000

    def show_merge_table(self):
        self._tonglian_init()
        sql = '''show create table {}; '''.format(self.merge_table_name)
        ret = self.tonglian_client.select_one(sql).get("Create Table")
        print(ret)
        '''
        CREATE TABLE `announcement_base` (
          `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
          `SecuCode` varchar(100) NOT NULL COMMENT '股票代码',
          `SecuAbbr` varchar(100) NOT NULL COMMENT '股票简称',
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='公告基础表'
        '''

    def process_secucode(self, data: dict):
        """secucode 加前缀

        规则:
        """
        secu_code = data.get("SecuCode")
        if secu_code.startswith("6"):
            data['SecuCode'] = "SH" + secu_code
        elif secu_code.startswith("3") or secu_code.startswith("0"):
            data['SecuCode'] = "SZ" + secu_code
        else:
            return None

        return data

    def load_his_ants(self):
        self._test_init()
        self._tonglian_init()

        for start in range(0, 5000):
            print()
            print()
            print("start: ", start)
            load_sql = '''select id, SecuCode, SecuAbbr, \
AntTime as PubDatetime1, AntTitle as Title1, AntDoc as PDFLink, CREATETIMEJZ as InsertDatetime1 \
from juchao_ant limit {}, {}; '''.format(start * self.batch_number, self.batch_number)
            print("sql is: ", load_sql)
            datas = self.test_client.select_all(load_sql)
            print("select count: ", len(datas))
            # 批量加前缀 并且去掉前缀不是  0 3 6 的
            datas = [self.process_secucode(data) for data in datas]
            datas = [data for data in datas if data is not None]
            if len(datas) != 0:
                save_count = self._batch_save(
                    self.tonglian_client, datas, self.merge_table_name,
                    ['SecuCode', 'SecuAbbr', 'PDFLink', 'PubDatetime1', 'InsertDatetime1', 'Title1'])
                print("save count: ", save_count)
            else:
                print("no more datas")
                break

    def load_his_live(self):
        self._test_init()
        self._tonglian_init()

        sql = '''select A.* from juchao_kuaixun A, juchao_ant B where A.code = B.SecuCode and A.link = B.AntDoc and A.type = '公告';  '''
        datas = self.test_client.select_all(sql)
        print("查询出 link 相同的数据个数是 : ", len(datas))

        for data in datas:
            print()
            print()
            print(data)
            sql = '''update {} set PubDatetime2 = '{}', InsertDatetime2 = '{}', Title2 = '{}' where PDFLink = '{}'; '''.format(
                self.merge_table_name, data.get("pub_date"), data.get("CREATETIMEJZ"), data.get("title"), data.get("link")
            )
            print(sql)
            count = self.tonglian_client.insert(sql)
            if count == 1:
                print("插入新数据 {}".format(data))
            elif count == 0:
                print("已有数据 {} ".format(data))
            else:
                print("count is {}".format(count))
            self.tonglian_client.end()

    def load_inc(self):
        self._spider2_init()
        self._tonglian_init()
        deadline = datetime.datetime.now() - datetime.timedelta(days=2)

        load_sql = '''select id, SecuCode, SecuAbbr, AntTime as PubDatetime1, AntTitle as Title1, AntDoc as PDFLink, \
CREATETIMEJZ as InsertDatetime1 from juchao_ant where UPDATETIMEJZ > '{}'; '''.format(deadline)
        print("sql is: ", load_sql)
        datas = self.r_spider_client.select_all(load_sql)
        print(len(datas))
        # 批量加前缀 并且去掉前缀不是  0 3 6 的
        datas = [self.process_secucode(data) for data in datas]
        datas = [data for data in datas if data is not None]

        if len(datas) != 0:
            save_count = self._batch_save(
                self.tonglian_client, datas, self.merge_table_name,
                ['SecuCode', 'SecuAbbr', 'PDFLink', 'PubDatetime1', 'InsertDatetime1', 'Title1'])
            print("save count: ", save_count)
        else:
            print("no selected datas")

        update_sql = '''select A.* from juchao_kuaixun A, juchao_ant B where A.pub_date > '{}' \
and A.code = B.SecuCode and A.link = B.AntDoc and A.type = '公告';  '''.format(deadline)
        print("kuaixun update sql is: ", update_sql)
        datas = self.r_spider_client.select_all(update_sql)
        print(len(datas))
        for data in datas:
            # print()
            # print()
            # print(data)
            sql = '''update {} set PubDatetime2 = '{}', InsertDatetime2 = '{}', Title2 = '{}' where PDFLink = '{}'; '''.format(
                self.merge_table_name, data.get("pub_date"), data.get("CREATETIMEJZ"), data.get("title"),
                data.get("link")
            )
            # print(sql)
            count = self.tonglian_client.insert(sql)
            if count == 1:
                print("插入新数据 {}".format(data))
            elif count == 0:
                print("已有数据 {} ".format(data))
            else:
                print("count is {}".format(count))
            self.tonglian_client.end()

    def start(self):
        # self.load_his_ants()

        # self.load_his_live()

        self.load_inc()


def task():
    MergeBase().start()
    for i in range(5):
        print()


if __name__ == '__main__':
    task()

    schedule.every(2).minutes.do(task)

    while True:
        schedule.run_pending()

        time.sleep(5)
