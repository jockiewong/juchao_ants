from base_spider import SpiderBase
from history_ants import JuChaoSearch


class AntSpider(SpiderBase):
    def __init__(self):
        super(AntSpider, self).__init__()
        self.tool_table_name = 'juchao_codemap'
        pass

    def start(self):
        self._spider_init()
        sql = '''select code, orgId from {}; '''.format(self.tool_table_name)
        ret = self.spider_client.select_all(sql)
        for r in ret:
            code_str = "{},{}".format(r.get("code"), r.get("orgId"))
            print(code_str)
            JuChaoSearch(code_str).start()


if __name__ == '__main__':
    AntSpider().start()
