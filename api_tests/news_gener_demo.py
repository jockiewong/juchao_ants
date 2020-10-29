# 接新闻数据源 -->  news_base_tonglian(良哥) --> dc_ann_event_source_news_detail

# 新闻先直接接通联库的数据
import json
import sys

import requests

from base_spider import SpiderBase


class NewsGenerator(SpiderBase):
    # vnews_content_v1  标题
    # vnews_body_v1  内容

    def __init__(self):
        super(NewsGenerator, self).__init__()
        self.content_table_name = 'vnews_content_v1'
        self.body_table_name = 'vnews_body_v1'

    def post_api(self, data: dict):
        data = {'texttype': 'news',
                'title': data.get("NEWS_TITLE"),
                'content': data.get("NEWS_BODY"),
                'prolist': ['event_news']
                }
        data_json = json.dumps(data)
        try:
            resp = requests.post('http://139.159.245.37:9009/jznlpsv/v2/query/', data_json)
        except Exception as e:
            print(e)
            resp = None
        if resp and resp.status_code == 200:
            body = json.loads(resp.text)
            print(body)

    def select_max_title_id(self):
        # 以标题中的新闻id为准
        self._tonglian_init()
        sql = '''select max(NEWS_ID) as max_id from {} ; '''.format(self.content_table_name)
        max_id = self.tonglian_client.select_one(sql).get("max_id")
        return max_id

    def launch(self):
        self._tonglian_init()
        max_id = self.select_max_title_id()
        # print(max_id)    # 78182211

        sql = '''select T.NEWS_TITLE, B.NEWS_BODY from vnews_content_v1 T, vnews_body_v1 B \
where T.NEWS_ID <= {} and T.NEWS_ID >= {} \
and B.NEWS_ID <= {} and B.NEWS_ID >= {}  \
and  T.NEWS_ID = B.NEWS_ID; '''
        datas = self.tonglian_client.select_all(sql)
        for data in datas:
            self.post_api(data)
            print()


if __name__ == '__main__':
    NewsGenerator().launch()
