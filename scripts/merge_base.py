import os
import sys

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from base_spider import SpiderBase


class MergeBase(SpiderBase):
    def __init__(self):
        super(MergeBase, self).__init__()
        self.merge_table_name = 'announcement_base'

    def load_his_ants(self):
        self._spider_init()
        self._tonglian_init()
        for start in range(0, int(13308349/100) + 2):
            load_sql = '''select id, SecuCode, SecuAbbr, \
AntTime as PubDatetime1, AntTitle as Title1, AntDoc as PDFLink, CREATETIMEJZ as InsertDatetime1 \
from juchao_ant limit {}, 100; '''.format(start * 100)
            print(load_sql)
            datas = self.spider_client.select_all(load_sql)
            count = self._batch_save(
                self.tonglian_client, datas, self.merge_table_name,
                ['SecuCode', 'SecuAbbr', 'PDFLink', 'PubDatetime1', 'InsertDatetime1', 'Title1'])
            print(count)

    def show_merge_table(self):
        self._tonglian_init()
        sql = '''show create table {}; '''.format(self.merge_table_name)
        ret = self.tonglian_client.select_one(sql).get("Create Table")
        print(ret)
        '''
        CREATE TABLE `announcement_base` (
          `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
          `SecuCode` varchar(100) NOT NULL COMMENT '股票代码',
          `SecuAbbr` varchar(100) NOT NULL COMMENT '股票简称',
          `PDFLink` varchar(1000) DEFAULT NULL COMMENT '公告pdf地址',
          `PubDatetime1` datetime NOT NULL COMMENT '公告发布时间(巨潮公告速递栏目中的时间)',
          `InsertDatetime1` datetime NOT NULL COMMENT '爬虫入库时间(巨潮公告速递栏目)',
          `Title1` varchar(1000) NOT NULL COMMENT '巨潮公告速递栏目中的标题',
          `PubDatetime2` datetime DEFAULT NULL COMMENT '公告发布时间(巨潮快讯栏目中的时间)',
          `InsertDatetime2` datetime DEFAULT NULL COMMENT '爬虫入库时间(巨潮快递栏目)',
          `Title2` varchar(1000) DEFAULT NULL COMMENT '巨潮快讯栏目中的标题（没有则留空）',
          `CreateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
          `UpdateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
          PRIMARY KEY (`id`),
          UNIQUE KEY `un1` (`PDFLink`),
          KEY `k1` (`SecuCode`,`PubDatetime1`,`PubDatetime2`,`UpdateTime`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='公告基础表'
        '''

    def start(self):


        pass


if __name__ == '__main__':
    # MergeBase().show_merge_table()
    MergeBase().load_his_ants()


'''
cd ../ 
docker build -f Dockerfile_merge -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_merge:v1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_merge:v1 
sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_merge:v1 
sudo docker run --log-opt max-size=10m --log-opt max-file=3 \
-itd --name ant_merge --env LOCAL=0 registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_merge:v1
'''