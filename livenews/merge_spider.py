# import datetime
# import json
# import os
# import sys
# import time
# import requests
#
# cur_path = os.path.split(os.path.realpath(__file__))[0]
# file_path = os.path.abspath(os.path.join(cur_path, ".."))
# sys.path.insert(0, file_path)
#
# from base_spider import SpiderBase
#
#
# org_tablecode_map = {
#     "juchao_kuaixun": ['巨潮快讯', 1060, ],
#     'xueqiu_livenews': ['雪球快讯', 1074, ],
# }
#
#
# class MergeJuchaoDayNews(SpiderBase):
#     def __init__(self):
#         super(MergeJuchaoDayNews, self).__init__()
#         self.web_url = 'http://www.cninfo.com.cn/new/commonUrl/quickNews?url=/disclosure/quickNews&queryDate=2020-08-13'
#         self.api_url = 'http://www.cninfo.com.cn/new/quickNews/queryQuickNews?queryDate={}&type='
#         self.fields = ['code', 'name', 'link', 'title', 'type', 'pub_date']
#         self.table_name = 'juchao_kuaixun'
#         info = org_tablecode_map.get(self.table_name)
#         self.name, self.table_code = info[0], info[1]
#         self._juyuan_init()
#         self._spider_init()
#
#     def get_secu_abbr(self, code):
#         sql = '''select SecuAbbr from secumain where secucode = '{}';'''.format(code)
#         name = self.juyuan_client.select_one(sql).get("SecuAbbr")
#         return name
#
#     def run(self):
#         self._spider_init()
#         end_day = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)
#         start_day = end_day - datetime.timedelta(days=1)
#
#         _day = start_day
#         while _day <= end_day:
#             _day_str = _day.strftime("%Y-%m-%d")
#             resp = requests.get(self.api_url.format(_day_str), headers=self.headers)
#             if resp and resp.status_code == 200:
#                 text = resp.text
#                 datas = json.loads(text)
#                 if not datas:
#                     print("{} 无公告数据".format(_day_str))
#                 else:
#                     for data in datas:
#                         item = dict()
#                         # 需要保存的字段: 快讯的发布详细时间、类型、标题、地址、股票代码、股票名称
#                         announcementTime = time.localtime(int(data.get("announcementTime") / 1000))
#                         announcementTime = time.strftime("%Y-%m-%d %H:%M:%S", announcementTime)
#                         item['PubDatetime'] = announcementTime
#                         item['InnerType'] = data.get("type")
#                         # item['Title'] = data.get("title")
#                         item['Title'] = '快讯'
#                         title = data.get("title")
#                         item['Content'] = title
#                         item['Website'] = data.get("pagePath")
#                         code = data.get("code")
#                         if code:
#                             item['SecuCode'] = code
#                             item['SecuAbbr'] = self.get_secu_abbr(code)
#                         # 增加合并表的字段
#                         item['DupField'] = "{}_{}".format(self.table_code, title)
#                         item['MedName'] = self.name
#                         item['OrgMedName'] = self.name
#                         item['OrgTableCode'] = self.table_code
#                         self._save(self.spider_client, item, self.merge_table, self.merge_fields)
#             _day += datetime.timedelta(days=1)
#             time.sleep(2)
