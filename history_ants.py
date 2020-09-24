import datetime
import json
import time

import requests

from base_spider import SpiderBase


class JuChaoSearch(SpiderBase):
    def __init__(self, stock_string):
        """
        查询单个 stock 的历史公告
        :param stock_string: eg.000001,gssz0000001
        """
        super(JuChaoSearch, self).__init__()
        self.stock_string = stock_string
        self.table_name = 'juchao_ant'
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
          `AntId` int(11) NOT NULL COMMENT '巨潮自带公告 ID', 
          `AntTime` datetime NOT NULL COMMENT '发布时间',
          `AntTitle` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '资讯标题',
          `AntDoc` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '公告详情页链接',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `ant_id` (`AntId`),
          UNIQUE KEY `code_doc` (`SecuCode`,`AntDoc`),
          KEY `ant_time` (`AntTime`),
          KEY `update_time` (`UPDATETIMEJZ`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='巨潮个股公告关联';  
        '''.format(self.table_name)
        self._spider_init()
        self.spider_client.insert(sql)
        self.spider_client.end()

    def query_history(self, start_date=None):
        if start_date is None:
            start_date = "2000-01-01"
        end_date = datetime.datetime.today().strftime("%Y-%m-%d")
        se_date = "{}~{}".format(start_date, end_date)
        print(se_date)
        for page in range(1000):
            time.sleep(1)
            print()
            print()
            print()
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
            resp = requests.post(self.api, headers=self.headers, data=post_data)
            if resp.status_code == 200:
                text = resp.text
                py_datas = json.loads(text)
                ants = py_datas.get("announcements")
                if ants is None:
                    return
                for ant in ants:
                    item = dict()
                    item['SecuCode'] = ant.get('secCode')
                    item['SecuAbbr'] = ant.get('secName')
                    item['AntId'] = ant.get("announcementId")
                    item['AntTitle'] = ant.get("announcementTitle")
                    time_stamp = ant.get("announcementTime") / 1000
                    item.update({'AntTime': datetime.datetime.fromtimestamp(time_stamp)})
                    item.update({'AntDoc': 'http://static.cninfo.com.cn/' + ant.get("adjunctUrl")})
                    self._save(self.spider_client, item, self.table_name, self.fields)
            else:
                print(resp)

    def start(self):
        self.create_history_table()
        self.query_history()


if __name__ == '__main__':
    JuChaoSearch("002080,9900001282").start()
    pass
