from base_spider import SpiderBase
from history_ants import JuChaoSearch


class AntSpider(SpiderBase):
    def __init__(self):
        super(AntSpider, self).__init__()
        pass

    def start(self):
        # TODO 解决程序断开的问题
        self._spider_init()
        sql = '''select code, orgId from {}; '''.format(self.tool_table_name)
        ret = self.spider_client.select_all(sql)
        for r in ret:
            code, org_id = r.get("code"), r.get("OrgId")
            # sql2 = '''select count(*) as count from {} where code = {}; '''.format(code, org_id)
            code_str = "{},{}".format(code, org_id)
            print(code_str)
            JuChaoSearch(code_str).start()


if __name__ == '__main__':
    AntSpider().start()
