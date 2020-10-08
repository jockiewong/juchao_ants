import datetime
import json
import requests
from retrying import retry

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
            start_date = "2000-01-01"
        end_date = datetime.datetime.today().strftime("%Y-%m-%d")
        se_date = "{}~{}".format(start_date, end_date)
        print(se_date)
        for page in range(1000):
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
            resp = requests.post(self.api, headers=self.headers, data=post_data, timeout=3)
            if resp.status_code == 200:
                text = resp.text
                print(text)
                py_datas = json.loads(text)
                web_count = py_datas.get("totalAnnouncement")
                exist_count = self.get_exist_count()
                print("web", web_count)
                print("exist", exist_count)
                if web_count == exist_count or (web_count - exist_count < 10):
                    print("当前证券历史已导入")
                    return

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
        self.query_history()


if __name__ == '__main__':
    JuChaoSearch("002080,9900001282").start()
    # JuChaoSearch("000671,gssz0000671").start()
    pass
