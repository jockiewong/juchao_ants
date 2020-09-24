import requests
from retrying import retry

from base_spider import SpiderBase
from history_ants import JuChaoSearch
from scripts.generate_juchao_codemap import JuChaoCodeMap


class AntSpider(SpiderBase):
    def __init__(self):
        super(AntSpider, self).__init__()
        pass

    @retry(stop_max_attempt_number=30)
    def start(self):
        # JuChaoCodeMap().start()

        self._spider_init()
        sql = '''select code, orgId from {} order by rand() ; '''.format(self.tool_table_name)
        ret = self.spider_client.select_all(sql)
        for r in ret:
            code, org_id = r.get("code"), r.get("orgId")
            code_str = "{},{}".format(code, org_id)
            print(code_str)
            JuChaoSearch(code_str).start()


if __name__ == '__main__':
    AntSpider().start()


'''
docker build -f Dockerfile -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_ant:v1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_ant:v1 
sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_ant:v1 
sudo docker run --log-opt max-size=10m --log-opt max-file=3 \
-itd --name ant --env LOCAL=0 registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_ant:v1
'''