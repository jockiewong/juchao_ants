import json
import pprint

import requests

from base_spider import SpiderBase


class AnnGenerator(SpiderBase):
    def __init__(self):
        super(AnnGenerator, self).__init__()
        self.api = "http://139.159.245.37:9009/jznlpsv/v2/query/"

    def fetch_datas(self):
        self._spider2_init()
        sql = '''select Title from juchao_kuaixun limit 100; '''
        datas = self.r_spider_client.select_all(sql)

        for data in datas:
            title = data.get("Title")
            data = {
                'texttype': 'ann',
                'title': title,
                'content': title,
                'prolist': ['event_ann'],
            }
            yield data

    def start(self):
        save_items = []
        for data in self.fetch_datas():
            print(data)
            data_json = json.dumps(data).encode('utf8')
            resp = requests.post(self.api, data_json)
            item = json.loads(resp.text)
            print(item)
            print()
            if item.get("event_ann"):
                save_items.append(item)

        print(len(save_items))


if __name__ == '__main__':
    AnnGenerator().start()

    # AnnGenerator().fetch_datas()

    pass
