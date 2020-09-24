import json
import time

import requests

from base_spider import SpiderBase


class JuChaoCodeMap(SpiderBase):
    def __init__(self):
        super(JuChaoCodeMap, self).__init__()
        self.fields = ['code', 'orgId', 'category', 'pinyin', 'zwjc']

    def create_tools_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS `juchao_codemap` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `code` varchar(8) NOT NULL COMMENT '证券代码',
            `orgId` varchar(16) NOT NULL COMMENT '证券编码',
            `category` varchar(8) NOT NULL COMMENT '证券分类',
            `pinyin` varchar(10) NOT NULL COMMENT '证券中文名拼音',
            `zwjc` varchar(20) NOT NULL COMMENT '证券中文名',
            `count` int(11) NOT NULL DEFAULT 0 COMMENT '当前入库公告个数', 
            `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
            `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (`id`),
            UNIQUE KEY `orgId_code` (`orgId`, `code`),
            KEY `update_time` (`UPDATETIMEJZ`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='巨潮证券编码';
        '''
        # alter table juchao_codemap add `count` int(11) NOT NULL DEFAULT 0 COMMENT '当前入库公告个数';
        self._spider_init()
        self.spider_client.insert(sql)
        self.spider_client.end()

    def get_stock_json(self):
        api = 'http://www.cninfo.com.cn/new/data/szse_a_stock.json?_={}'.format(int(time.time() * 1000))
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'www.cninfo.com.cn',
            'Origin': 'http://uc.cninfo.com.cn',
            'Pragma': 'no-cache',
            'Referer': 'http://uc.cninfo.com.cn/user/optionalConfig?groupId=88937',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
        }
        resp = requests.get(api, headers=headers)
        if resp and resp.status_code == 200:
            text = resp.text
            try:
                py_data = json.loads(text).get("stockList")
            except:
                print(text)
                raise Exception("resp parse error.")

            self._spider_init()
            for one in py_data:
                self._save(self.spider_client, one, self.tool_table_name, self.fields)

    def start(self):
        self.create_tools_table()
        self.get_stock_json()


if __name__ == '__main__':
    JuChaoCodeMap().start()
