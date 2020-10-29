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
        self.batch_num = 10000

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
        sql = '''select min(NEWS_ID) as min_id, max(NEWS_ID) as max_id from {} ; '''.format(self.content_table_name)
        data = self.tonglian_client.select_one(sql)
        max_id, min_id = data.get("max_id"), data.get("min_id")
        return max_id, min_id

    def launch(self):
        self._tonglian_init()
        max_id, min_id = self.select_max_title_id()
        print(max_id, " ", min_id)
        for i in range(min_id // self.batch_num, max_id // self.batch_num + 1):
            news_id_start = self.batch_num * i
            news_id_end = self.batch_num * (i+1)
            print(news_id_start, news_id_end)
            sql = '''select T.NEWS_TITLE, B.NEWS_BODY from vnews_content_v1 T, vnews_body_v1 B \
where T.NEWS_ID >= {} and T.NEWS_ID <= {} \
and B.NEWS_ID >= {} and B.NEWS_ID <= {}  \
and T.NEWS_ID = B.NEWS_ID; '''.format(news_id_start, news_id_end, news_id_start, news_id_end)
            datas = self.tonglian_client.select_all(sql)
            print(len(datas))
            # for data in datas:
            #     self.post_api(data)


if __name__ == '__main__':
    NewsGenerator().launch()
