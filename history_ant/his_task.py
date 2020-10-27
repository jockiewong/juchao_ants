import datetime
import json
import os
import sys
import time

import requests
import schedule
from retrying import retry

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from base_spider import SpiderBase
from history_ant.history_ants import JuChaoSearch


class AntSpider(SpiderBase):
    def __init__(self):
        super(AntSpider, self).__init__()

    def start(self):
        # JuChaoCodeMap().start()
        self._spider_init()
        # sql = '''select code, orgId from {} order by rand() ; '''.format(self.tool_table_name)
        sql = '''select id, code, orgId from {} order by id; '''.format(self.tool_table_name)
        ret = self.spider_client.select_all(sql)
        for r in ret:
            order_id, code, org_id = r.get('id'), r.get("code"), r.get("orgId")
            code_str = "{},{}".format(code, org_id)
            print()
            print()
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
            print()
            print()
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
            if resp.status_code == 200:
                text = resp.text
                # print(text, text is None, text == '')
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
                    self._save(self.spider_client, item, self.history_table_name, self.fields)
            else:
                print(resp)


if __name__ == '__main__':
    LaunchSpider().launch()
    # AntSpider().start()
    AntSpider().ding_inc_count()

    # schedule.every(20).minutes.do(AntSpider().start)
    schedule.every(10).minutes.do(LaunchSpider().launch)
    schedule.every(5).hours.do(AntSpider().ding_inc_count)

    while True:
        schedule.run_pending()
        time.sleep(10)
