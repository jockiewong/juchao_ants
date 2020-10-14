import time
import schedule

from base_spider import SpiderBase
from history_ants import JuChaoSearch
from scripts.generate_juchao_codemap import JuChaoCodeMap


class AntSpider(SpiderBase):
    def __init__(self):
        super(AntSpider, self).__init__()
        pass

    def start(self):
        # JuChaoCodeMap().start()

        self._spider_init()
        # sql = '''select code, orgId from {} order by rand() ; '''.format(self.tool_table_name)
        sql = '''select id, code, orgId from {} order by id; '''.format(self.tool_table_name)
        ret = self.spider_client.select_all(sql)
        for r in ret:
            order_id, code, org_id = r.get('id'), r.get("code"), r.get("orgId")
            # if code in ('000671', '002183', '600340', ):
            #     continue

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


if __name__ == '__main__':
    AntSpider().start()
    AntSpider().ding_inc_count()

    # schedule.every(20).minutes.do(AntSpider().start)
    # schedule.every(5).hours.do(AntSpider().ding_inc_count)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(10)


'''
docker build -f Dockerfile -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_ant:v1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_ant:v1 
sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_ant:v1 
sudo docker run --log-opt max-size=10m --log-opt max-file=3 \
-itd --name ant --env LOCAL=0 registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_ant:v1
'''
