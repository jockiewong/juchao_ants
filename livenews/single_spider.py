# import datetime
# import json
# import os
# import sys
# import time
# import traceback
#
# import requests
# import schedule
# from retrying import retry
#
# cur_path = os.path.split(os.path.realpath(__file__))[0]
# file_path = os.path.abspath(os.path.join(cur_path, ".."))
# sys.path.insert(0, file_path)
#
# from base_spider import SpiderBase
#
#
# class SingleJuchaoDayNews(SpiderBase):
#     def __init__(self):
#         super(SingleJuchaoDayNews, self).__init__()
#         self.web_url = 'http://www.cninfo.com.cn/new/commonUrl/quickNews?url=/disclosure/quickNews&queryDate=2020-08-13'
#         self.api_url = 'http://www.cninfo.com.cn/new/quickNews/queryQuickNews?queryDate={}&type='
#
#         self.fields = ['code', 'name', 'link', 'title', 'type', 'pub_date']
#         self.table_name = 'juchao_kuaixun'
#         self.name = '巨潮快讯'
#         self._juyuan_init()
#         self._spider_init()
#
#     def get_secu_abbr(self, code):
#         sql = '''select SecuAbbr from secumain where secucode = '{}';'''.format(code)
#         name = self.juyuan_client.select_one(sql).get("SecuAbbr")
#         return name
#
#     def _create_table(self):
#         sql = '''
#          CREATE TABLE IF NOT EXISTS `{}` (
#           `id` int(11) NOT NULL AUTO_INCREMENT,
#           `code` varchar(8) DEFAULT NULL COMMENT '证券代码',
#           `name` varchar(16) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '证券简称',
#           `pub_date` datetime NOT NULL COMMENT '发布时间',
#           `title` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '资讯标题',
#           `type` varchar(16) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '资讯类别',
#           `link` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '公告详情页链接',
#           `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
#           `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#           PRIMARY KEY (`id`),
#           UNIQUE KEY `date_title` (`pub_date`, `title`),
#           KEY `pub_date` (`pub_date`),
#           KEY `update_time` (`UPDATETIMEJZ`)
#         ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='{}';
#         '''.format(self.table_name, self.name)
#         self.spider_client.insert(sql)
#         self.spider_client.end()
#
#     def get_redit_link(self, link):
#         resp = self.my_get(link)
#         redit_list = resp.history
#         try:
#             redit_link = redit_list[len(redit_list) - 1].headers["location"]
#         except IndexError:
#             redit_link = link
#         except:
#             return None
#         return redit_link
#
#     def if_final_link(self, link: str):
#         if link.endswith("PDF"):
#             return True
#         else:
#             return False
#
#     @retry(stop_max_attempt_number=5)
#     def my_get(self, link):
#         print('get in .. ')
#         resp = requests.get(link, headers=self.headers, timeout=5)
#         return resp
#
#     def start(self):
#         self._create_table()
#         end_day = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)
#         # 历史(貌似是只有最近半年的)
#         # start_day = datetime.datetime(2020, 6, 1)
#         start_day = end_day    # 定时增量
#
#         _day = start_day
#         while _day <= end_day:
#             _day_str = _day.strftime("%Y-%m-%d")
#             resp = self.my_get(self.api_url.format(_day_str))
#             print("resp: ", resp)
#             if resp and resp.status_code == 200:
#                 text = resp.text
#                 print(text)
#                 datas = json.loads(text)
#                 if not datas:
#                     print("{} 无公告数据".format(_day_str))
#                 else:
#                     # 保存数据
#                     items = []
#                     for data in datas:
#                         print(data)
#                         item = {}
#                         # 需要保存的字段: 快讯的发布详细时间、类型、标题、地址、股票代码、股票名称
#                         announcementTime = time.localtime(int(data.get("announcementTime") / 1000))
#                         announcementTime = time.strftime("%Y-%m-%d %H:%M:%S", announcementTime)
#                         item['pub_date'] = announcementTime
#
#                         item['type'] = data.get("type")
#                         item['title'] = data.get("title")
#                         page_path = data.get("pagePath")
#                         if page_path is None:
#                             link = '''http://www.cninfo.com.cn/new/disclosure/detail?stock=&announcementId={}&announcementTime={}'''.format(
#                                 data.get("textId"), _day_str)
#                         else:
#                             try:
#                                 link = self.get_redit_link(page_path)
#                             except:
#                                 link = None
#                         if not link:
#                             continue
#                         item['link'] = link
#                         code = data.get("code")
#                         if code:
#                             item['code'] = code
#                             item['name'] = self.get_secu_abbr(code)
#                         print(item)
#                         items.append(item)
#                         print()
#                     self._batch_save(self.spider_client, items, self.table_name, self.fields)
#             _day += datetime.timedelta(days=1)
#
#
# def my_task():
#     try:
#         SingleJuchaoDayNews().start()
#     except:
#         traceback.print_exc()
#
#
# if __name__ == '__main__':
#     schedule.every(30).seconds.do(my_task)
#
#     while True:
#         schedule.run_pending()
#         time.sleep(10)
