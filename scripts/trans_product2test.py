import datetime
import os
import sys
import time

import schedule

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from base_spider import SpiderBase


class DataTranser(SpiderBase):
    """将测试库与线上的正式库保持一致 """
    def __init__(self):
        super(DataTranser, self).__init__()
        self.batch_number = 1000

    def tracking(self):
        """实时追踪 并保持两个数据库一致 """
        self._spider_init()
        self._test_init()
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(minutes=10)

        sql = '''select count(*)  from juchao_ant where UPDATETIMEJZ > '{}' and UPDATETIMEJZ < '{}';'''.format(
            start_time, end_time)
        print("sql: ", sql)
        datas = self.spider_client.select_all(sql)
        save_count = self._batch_save(self.test_client, datas, 'juchao_ant',
                         ['id',  'SecuCode', 'SecuAbbr', 'AntId', 'AntTime', 'AntTitle', 'AntDoc'])
        print("save count:", save_count)

    def start(self):
        self._spider_init()
        self._test_init()

        # csql = '''
        #     CREATE TABLE IF NOT EXISTS `juchao_ant` (
        #       `id` int(11) NOT NULL AUTO_INCREMENT,
        #       `SecuCode` varchar(8) NOT NULL COMMENT '证券代码',
        #       `SecuAbbr` varchar(16) NOT NULL COMMENT '证券代码',
        #       `AntId` int(20) NOT NULL COMMENT '巨潮自带公告 ID',
        #       `AntTime` datetime NOT NULL COMMENT '发布时间',
        #       `AntTitle` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '资讯标题',
        #       `AntDoc` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '公告详情页链接',
        #       `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
        #       `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        #       PRIMARY KEY (`id`),
        #       UNIQUE KEY `ant_id` (`AntId`),
        #       KEY `ant_time` (`AntTime`),
        #       KEY `secucode` (`SecuCode`),
        #       KEY `update_time` (`UPDATETIMEJZ`)
        #     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='巨潮个股公告关联' ;
        # '''
        # self.test_client.insert(csql)

        for start in range(5000):
            sql = '''select * from juchao_ant limit {}, {};'''.format(start*self.batch_number, self.batch_number)
            print("sql: ", sql)
            datas = self.spider_client.select_all(sql)
            print('select count: ', len(datas))
            if len(datas) == 0:
                break
            save_count = self._batch_save(self.test_client, datas, 'juchao_ant',
                                          ['id',  'SecuCode', 'SecuAbbr', 'AntId', 'AntTime', 'AntTitle', 'AntDoc'])
            print("save count:", save_count)

        # csql = '''
        # CREATE TABLE IF NOT EXISTS `juchao_kuaixun` (
        #   `id` int(11) NOT NULL AUTO_INCREMENT,
        #   `code` varchar(8) DEFAULT NULL COMMENT '证券代码',
        #   `name` varchar(16) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '证券简称',
        #   `pub_date` datetime NOT NULL COMMENT '发布时间',
        #   `title` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '资讯标题',
        #   `type` varchar(16) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '资讯类别',
        #   `link` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '公告详情页链接',
        #   `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
        #   `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        #   PRIMARY KEY (`id`),
        #   UNIQUE KEY `date_title` (`pub_date`,`title`),
        #   KEY `pub_date` (`pub_date`),
        #   KEY `update_time` (`UPDATETIMEJZ`)
        # ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='巨潮快讯';
        # '''
        # self.test_client.insert(csql)

        for start in range(20):
            sql = '''select * from juchao_kuaixun limit {}, {}; '''.format(start*self.batch_number, self.batch_number)
            print(sql)
            datas = self.spider_client.select_all(sql)
            print("select count:", len(datas))
            if len(datas) == 0:
                break
            save_count = self._batch_save(self.test_client, datas, 'juchao_kuaixun',
                                          ['id', 'code', 'name', 'pub_date', 'title', 'type', 'link'])
            print("save count: ", save_count)


def task():
    DataTranser().start()


if __name__ == '__main__':
    schedule.every(3).minutes.do(task)
    while True:
        schedule.run_pending()
        time.sleep(10)


'''cd ../ 
docker build -f Dockerfile_load -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_load:v1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_load:v1 
sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_load:v1 
sudo docker run --log-opt max-size=10m --log-opt max-file=3 \
-itd --name load --env LOCAL=0 registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_load:v1
'''
