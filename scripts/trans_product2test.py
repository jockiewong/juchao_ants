import os
import sys
import time

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from base_spider import SpiderBase


class DataTranser(SpiderBase):

    def __init__(self):
        super(DataTranser, self).__init__()
        self.batch_number = 1000

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
            save_count = self._batch_save(self.test_client, datas, 'juchao_ant',
                                          ['id',  'SecuCode', 'SecuAbbr', 'AntId', 'AntTime', 'AntTitle', 'AntDoc'])
            print("save count:", save_count)


if __name__ == '__main__':
    DataTranser().start()


'''cd ../ 
docker build -f Dockerfile_load -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_load:v1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_load:v1 
sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_load:v1 
sudo docker run --log-opt max-size=10m --log-opt max-file=3 \
-itd --name load --env LOCAL=0 registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_load:v1
'''
