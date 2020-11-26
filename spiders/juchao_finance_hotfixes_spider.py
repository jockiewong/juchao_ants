import datetime
import json
import os
import sys
import time

import requests
import retrying

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from configs import (SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, SPIDER_MYSQL_PASSWORD,
                     SPIDER_MYSQL_DB, )
from sql_base import Connection


class JuchaoFinanceSpider(object):
    """巨潮历史公告爬虫 """
    def __init__(self):
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
        self._spider_conn = Connection(
            host=SPIDER_MYSQL_HOST,
            port=SPIDER_MYSQL_PORT,
            user=SPIDER_MYSQL_USER,
            password=SPIDER_MYSQL_PASSWORD,
            database=SPIDER_MYSQL_DB,
        )
        self.history_table_name = 'juchao_ant_finance'  # 巨潮历史公告(财务相关)表

    def _create_table(self):
        create_sql = '''
         CREATE TABLE IF NOT EXISTS `juchao_ant_finance` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `SecuCode` varchar(8) NOT NULL COMMENT '证券代码',
          `SecuAbbr` varchar(16) NOT NULL COMMENT '证券代码',
          `Category` varchar(32) NOT NULL COMMENT '财报类型',
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='巨潮个股财务类公告' ; 
        '''
        self._spider_conn.insert(create_sql)

    @retrying.retry(stop_max_attempt_number=10)
    def my_post(self, link: str, post_data):
        resp = requests.post(link, headers=self.headers, data=post_data, timeout=10)
        return resp

    def start(self, start_date=None, end_date=None):
        '''网站限制 一次最多只有一年的数据'''
        self._create_table()

        if start_date is None:
            start_date = datetime.datetime.today() - datetime.timedelta(days=10)
        if end_date is None:
            end_date = datetime.datetime.today()

        se_date = "{}~{}".format(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        print(se_date)

        for page in range(10):
            print("page >> {}".format(page))
            for category in ('category_ndbg_szsh',
                             'category_bndbg_szsh',
                             'category_yjdbg_szsh',
                             'category_sjdbg_szsh',
                             'category_yjygjxz_szsh',
                             ):
                post_data = {
                    'pageNum': page,
                    'pageSize': 30,
                    'column': 'szse',
                    'tabName': 'fulltext',
                    'plate': '',
                    'stock': '',
                    'searchkey': '',
                    'secid': '',
                    # 财务包含以下几个版块: 年报、半年报、一季报、三季报、业绩预告
                    # 年报: category_ndbg_szsh
                    # 半年报: category_bndbg_szsh
                    # 一季报: category_yjdbg_szsh
                    # 三季报: category_sjdbg_szsh
                    # 业绩预告: category_yjygjxz_szsh
                    # 'category': 'category_ndbg_szsh;category_bndbg_szsh;category_yjdbg_szsh;category_sjdbg_szsh;category_yjygjxz_szsh',
                    'category': category,
                    'trade': '',
                    'seDate': se_date,
                    'sortName': '',
                    'sortType': '',
                    'isHLtitle': True,
                }
                # resp = requests.post(self.api, headers=self.headers, data=post_data, timeout=3)
                resp = self.my_post(self.api, post_data)
                if resp.status_code == 200:
                    text = resp.text
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
                        item['Category'] = category
                        time_stamp = ant.get("announcementTime") / 1000
                        item.update({'AntTime': datetime.datetime.fromtimestamp(time_stamp)})
                        item.update({'AntDoc': 'http://static.cninfo.com.cn/' + ant.get("adjunctUrl")})
                        print(item)
                        self._spider_conn.table_insert(self.history_table_name, item)
                else:
                    print(resp)


if __name__ == '__main__':
    while True:
        finance_his = JuchaoFinanceSpider()
        finance_his.start()
        time.sleep(180)
