'''需求: 2020-11-02 在dc_ann_event_source_news_detail 中增加媒体名称字段
CREATE TABLE `vnews_content_v1` (
  `NEWS_ID` bigint(20) NOT NULL DEFAULT '0',
  `INSERT_TIME` datetime DEFAULT NULL,
  `UPDATE_TIME` datetime DEFAULT NULL,
  `NEWS_ORIGIN_SOURCE` varchar(50) DEFAULT NULL,
  `NEWS_AUTHOR` varchar(500) DEFAULT NULL,
  `NEWS_URL` varchar(500) DEFAULT NULL,
  `NEWS_TITLE` varchar(300) DEFAULT NULL,
  `GROUP_ID` bigint(20) DEFAULT NULL,
  `NEWS_PUBLISH_SITE` varchar(50) DEFAULT NULL,
  `NEWS_PUBLISH_TIME` datetime DEFAULT NULL,
  `EFFECTIVE_TIME` datetime DEFAULT NULL,
  PRIMARY KEY (`NEWS_ID`) USING BTREE,
  KEY `public_time` (`NEWS_PUBLISH_TIME`),
  KEY `update_time` (`UPDATE_TIME`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;


CREATE TABLE `dc_ann_event_source_news_detail` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `NewsID` bigint(20) NOT NULL COMMENT '新闻主表ID',
  `MedName` varchar(100) DEFAULT NULL COMMENT '媒体名称',
  `PubTime` datetime NOT NULL COMMENT '发布时间（精确到秒）',
  `Title` varchar(500) DEFAULT NULL COMMENT '标题',
  `Website` varchar(1000) DEFAULT NULL COMMENT '网址',
  `SecuCode` varchar(20) DEFAULT NULL COMMENT '股票代码',
  `EventCode` varchar(20) DEFAULT NULL COMMENT '事件代码',
  `EventName` varchar(1000) DEFAULT NULL COMMENT '事件名称',
  `Position` tinyint(4) NOT NULL COMMENT '提及位置：1-标题,2-内容',
  `IsValid` tinyint(4) NOT NULL DEFAULT 1 COMMENT '是否有效',
  `CreateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `UpdateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `un1` (`NewsID`,`SecuCode`,`EventCode`),
  KEY `k1` (`NewsID`,`PubTime`,`SecuCode`,`EventCode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='公告舆情事件明细-新闻源';
'''
import os
import sys

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from base_spider import SpiderBase


class MedNameUpdate(SpiderBase):
    def __init__(self):
        super(MedNameUpdate, self).__init__()

    def launch(self):
        self._tonglian_init()
        self._yuqing_init()
        sql = '''select distinct(NewsID) from dc_ann_event_source_news_detail; '''
        news_id_list = self.yuqing_client.select_all(sql)
        news_id_list = tuple([one.get("NewsID") for one in news_id_list])
        news_medname_map = {}
        sql2 = '''select NEWS_ID, NEWS_ORIGIN_SOURCE from vnews_content_v1 where NEWS_ID in {}; '''.format(news_id_list)
        ret = self.tonglian_client.select_all(sql2)
        for r in ret:
            news_medname_map[r.get("NEWS_ID")] = r.get("NEWS_ORIGIN_SOURCE")

        print(news_medname_map)


if __name__ == '__main__':
    MedNameUpdate().launch()
