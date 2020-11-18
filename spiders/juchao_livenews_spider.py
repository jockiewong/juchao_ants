import datetime
import json
import os
import sys
import time
import requests
from retrying import retry

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from sql_base import Connection
from configs import (SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, SPIDER_MYSQL_PASSWORD,
                     SPIDER_MYSQL_DB, JUY_HOST, JUY_PORT, JUY_USER, JUY_PASSWD, JUY_DB)


class JuchaoLiveNewsSpider(object):
    """巨潮快讯爬虫"""
    def __init__(self):
        self.web_url = 'http://www.cninfo.com.cn/new/commonUrl/quickNews?url=/disclosure/quickNews&queryDate=2020-08-13'
        self.api_url = 'http://www.cninfo.com.cn/new/quickNews/queryQuickNews?queryDate={}&type='
        self.fields = ['code', 'name', 'link', 'title', 'type', 'pub_date']
        self.table_name = 'juchao_kuaixun'
        self.name = '巨潮快讯'
        self._spider_conn = Connection(
            host=SPIDER_MYSQL_HOST,
            port=SPIDER_MYSQL_PORT,
            user=SPIDER_MYSQL_USER,
            password=SPIDER_MYSQL_PASSWORD,
            database=SPIDER_MYSQL_DB,
        )
        self._juyuan_conn = Connection(
            host=JUY_HOST,
            port=JUY_PORT,
            user=JUY_USER,
            password=JUY_PASSWD,
            database=JUY_DB,
        )
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Chrome/79.0.3945.117 Safari/537.36'
        }

    def get_secu_abbr(self, code):
        """
        从聚源数据库获取证券代码对应的中文简称
        :param code: 无前缀的证券代码
        :return:
        """
        sql = f'''select SecuAbbr from secumain where secucode=%s;'''
        name = self._juyuan_conn.get(sql, code).get("SecuAbbr")
        return name

    def _create_table(self):
        """
        在爬虫数据库中进行巨潮快讯(juchao_kuaixun)的建表操作
        若已经建表则忽略
        :return:
        """
        sql = '''
         CREATE TABLE IF NOT EXISTS `{}` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `code` varchar(8) DEFAULT NULL COMMENT '证券代码',
          `name` varchar(16) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '证券简称', 
          `pub_date` datetime NOT NULL COMMENT '发布时间',
          `title` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '资讯标题',
          `type` varchar(16) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '资讯类别',
          `link` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '公告详情页链接',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `date_title` (`pub_date`, `title`),
          KEY `pub_date` (`pub_date`),
          KEY `update_time` (`UPDATETIMEJZ`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='{}'; 
        '''.format(self.table_name, self.name)
        self._spider_conn.execute(sql)

    def get_redit_link(self, link):
        """获取最终重定向后的网址"""
        resp = self.my_get(link)
        redit_list = resp.history
        try:
            redit_link = redit_list[len(redit_list) - 1].headers["location"]
        except IndexError:
            redit_link = link
        except:
            return None
        return redit_link

    @retry(stop_max_attempt_number=5)
    def my_get(self, link):
        """请求 超时\被ban 时重试"""
        print(f'get in {link} .. ')
        resp = requests.get(link, headers=self.headers, timeout=5)
        return resp

    def start(self):
        """启动入口"""
        self._create_table()
        end_day = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)
        # 历史(只有最近半年的)
        # start_day = datetime.datetime(2020, 6, 1)  # 确定一个历史的开始时间节点
        start_day = end_day    # 定时增量后每次只重刷当天的数据即可

        _day = start_day
        while _day <= end_day:
            _day_str = _day.strftime("%Y-%m-%d")
            resp = self.my_get(self.api_url.format(_day_str))
            if resp and resp.status_code == 200:
                text = resp.text
                datas = json.loads(text)
                if not datas:
                    print("{} 无公告数据".format(_day_str))
                else:
                    for data in datas:
                        print(data)
                        item = {}
                        # 需要保存的字段: 快讯的发布详细时间、类型、标题、地址、股票代码、股票名称
                        announcementTime = time.localtime(int(data.get("announcementTime") / 1000))
                        announcementTime = time.strftime("%Y-%m-%d %H:%M:%S", announcementTime)
                        item['pub_date'] = announcementTime

                        item['type'] = data.get("type")
                        item['title'] = data.get("title")
                        page_path = data.get("pagePath")
                        if page_path is None:
                            link = '''http://www.cninfo.com.cn/new/disclosure/detail?stock=&announcementId={}&announcementTime={}'''.format(
                                data.get("textId"), _day_str)
                        else:
                            try:
                                link = self.get_redit_link(page_path)
                            except:
                                link = None
                        if not link:
                            continue
                        item['link'] = link
                        code = data.get("code")
                        if code:
                            item['code'] = code    # 无前缀的证券代码
                            item['name'] = self.get_secu_abbr(code)
                        print(item)
                        self._spider_conn.table_insert(self.table_name, item)
            _day += datetime.timedelta(days=1)
