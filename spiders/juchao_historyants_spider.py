import datetime
import json
import os
import sys
import time
import traceback

import requests
import schedule
from retrying import retry

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from base_spider import SpiderBase


class JuChaoSearch(SpiderBase):
    def __init__(self, stock_string):
        """
        查询单个 stock 的历史公告
        :param stock_string: eg.000001,gssz0000001
        """
        super(JuChaoSearch, self).__init__()
        self.stock_string = stock_string
        self.fields = ['SecuCode', 'SecuAbbr', 'AntId', 'AntTime', 'AntTitle', 'AntDoc']
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'www.cninfo.com.cn',
            'Origin': 'http://www.cninfo.com.cn',
            'Pragma': 'no-cache',
            'Referer': 'http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&lastPage=index',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
        }
        self.api = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'

    def create_history_table(self):
        sql = '''
         CREATE TABLE IF NOT EXISTS `{}` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `SecuCode` varchar(8) NOT NULL COMMENT '证券代码',
          `SecuAbbr` varchar(16) NOT NULL COMMENT '证券代码',
          `AntId` int(20) NOT NULL COMMENT '巨潮自带公告 ID', 
          `AntTime` datetime NOT NULL COMMENT '发布时间',
          `AntTitle` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '资讯标题',
          `AntDoc` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '公告详情页链接',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `ant_id` (`AntId`),
          KEY `ant_time` (`AntTime`),
          KEY `secucode` (`SecuCode`),
          KEY `update_time` (`UPDATETIMEJZ`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='巨潮个股公告关联';  
        '''.format(self.history_table_name)
        self._spider_init()
        self.spider_client.insert(sql)
        self.spider_client.end()

    @retry(stop_max_attempt_number=30)
    def query_history(self, start_date=None):
        if start_date is None:
            start_date = datetime.datetime.today() - datetime.timedelta(days=10)
            # start_date = datetime.datetime(2020, 6, 1)

        end_date = datetime.datetime.today()
        se_date = "{}~{}".format(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        print(se_date)

        for page in range(100):
            post_data = {
                'pageNum': page,
                'pageSize': 30,
                'column': 'szse',
                'tabName': 'fulltext',
                'plate': '',     # 版块
                'stock': self.stock_string,
                'searchkey': '',    # 查询关键字
                'secid': '',
                'category': '',
                'trade': '',   # 行业分类
                'seDate': se_date,
                'sortName': '',
                'sortType': '',
                'isHLtitle': True,
            }
            resp = requests.post(self.api, headers=self.headers, data=post_data, timeout=3)
            if resp.status_code == 200:
                text = resp.text
                py_datas = json.loads(text)
                ants = py_datas.get("announcements")
                if ants is None:
                    break

                for ant in ants:
                    item = dict()
                    item['SecuCode'] = ant.get('secCode')
                    item['SecuAbbr'] = ant.get('secName')
                    item['AntId'] = ant.get("announcementId")
                    item['AntTitle'] = ant.get("announcementTitle")
                    time_stamp = ant.get("announcementTime") / 1000
                    item.update({'AntTime': datetime.datetime.fromtimestamp(time_stamp)})
                    item.update({'AntDoc': 'http://static.cninfo.com.cn/' + ant.get("adjunctUrl")})
                    self._save(self.spider_client, item, self.history_table_name, self.fields)
            else:
                print(resp)

    def get_exist_count(self):
        """
        检验网站个数与入库个数是否一致
        :return:
        """
        code = self.stock_string.split(",")[0]
        self._spider_init()
        sql = '''select count(*) as count from {} where SecuCode = {}; '''.format(self.history_table_name, code)
        ret = self.spider_client.select_one(sql)
        count = ret.get("count")
        return count

    def start(self):
        # self.create_history_table()
        self._spider_init()
        self.query_history()


class AntSpider(SpiderBase):
    def __init__(self):
        super(AntSpider, self).__init__()

    def start(self):
        self._spider_init()
        sql = '''select id, code, orgId from {} order by id; '''.format(self.tool_table_name)
        ret = self.spider_client.select_all(sql)
        for r in ret:
            order_id, code, org_id = r.get('id'), r.get("code"), r.get("orgId")
            code_str = "{},{}".format(code, org_id)
            print(order_id)
            print(code_str)
            JuChaoSearch(code_str).start()

    def ding_inc_count(self):
        self._spider_init()
        sql = '''SELECT count(id) as inc_count FROM {} WHERE {} > date_sub(CURDATE(), interval 1 day);'''.format(
            self.history_table_name, "AntTime")
        inc_count = self.spider_client.select_one(sql).get("inc_count")
        msg = '舆情猎手公告页面数据源【巨潮公告】今日截止目前\n按照公告发布时间 AntTime 新增 {}\n'.format(inc_count)

        sql2 = '''SELECT count(id) as inc_count FROM {} WHERE {} > date_sub(CURDATE(), interval 1 day);'''.format(
            self.history_table_name, "UPDATETIMEJZ")
        inc_count2 = self.spider_client.select_one(sql2).get("inc_count")

        msg += '按照插入时间 UPDATETIMEJZ 新增 {}\n'.format(inc_count2)
        print(msg)
        self.ding(msg)


class LaunchSpider(SpiderBase):
    def __init__(self):
        super(LaunchSpider, self).__init__()
        self.api = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
        self.fields = ['SecuCode', 'SecuAbbr', 'AntId', 'AntTime', 'AntTitle', 'AntDoc']
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'www.cninfo.com.cn',
            'Origin': 'http://www.cninfo.com.cn',
            'Pragma': 'no-cache',
            'Referer': 'http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&lastPage=index',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
        }

    def launch(self):
        self._spider_init()
        self.query_history()

    def my_fetch(self, method='GET'):
        pass

    def query_history(self, start_date=None):
        if start_date is None:
            start_date = datetime.datetime.today() - datetime.timedelta(days=10)

        end_date = datetime.datetime.today()
        se_date = "{}~{}".format(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        print(se_date)

        for page in range(1000):
            print("page >> {}".format(page))
            post_data = {
                'pageNum': page,
                'pageSize': 30,
                'column': 'szse',
                'tabName': 'fulltext',
                'plate': '',
                'stock': '',
                'searchkey': '',
                'secid': '',
                'category': '',
                'trade': '',
                'seDate': se_date,
                'sortName': '',
                'sortType': '',
                'isHLtitle': True,
            }
            resp = requests.post(self.api, headers=self.headers, data=post_data, timeout=3)
            print(resp)
            if resp.status_code == 200:
                text = resp.text
                # print(text)
                if text == '':
                    break

                py_datas = json.loads(text)
                ants = py_datas.get("announcements")
                if ants is None:
                    break

                for ant in ants:
                    item = dict()
                    item['SecuCode'] = ant.get('secCode')
                    item['SecuAbbr'] = ant.get('secName')
                    item['AntId'] = ant.get("announcementId")
                    item['AntTitle'] = ant.get("announcementTitle")
                    time_stamp = ant.get("announcementTime") / 1000
                    item.update({'AntTime': datetime.datetime.fromtimestamp(time_stamp)})
                    item.update({'AntDoc': 'http://static.cninfo.com.cn/' + ant.get("adjunctUrl")})
                    print(item)
                    print("SAVE RES: ", self._save(self.spider_client, item, self.history_table_name, self.fields))
            else:
                print(resp)


def my_task():
    try:
        LaunchSpider().launch()
    except:
        traceback.print_exc()
        time.sleep(10)


if __name__ == '__main__':
    my_task()
    schedule.every(10).minutes.do(my_task)
    while True:
        schedule.run_pending()
        time.sleep(10)
