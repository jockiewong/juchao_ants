## 舆情猎手公告页面


### 爬虫页面[spiders]
- 从巨潮历史资讯和巨潮快讯获取爬虫数据 


### 公告基础数据[source]
- 巨潮历史资讯表/巨潮快讯表 --> merge -->  announcement_base.py


### 中间表模块[middle_tables]
- 股吧基础数据（爬虫库 guba_bade ）--> model --> dc_ann_event_source_guba_detail 表 
- 通联新闻数据                    --> model --> dc_ann_event_source_news_detail 表 
- announcement_base 表           --> model --> dc_ann_event_source_ann_detail  表


### 汇总表[final_summary]

    dc_ann_event_source_guba_detail -->
    dc_ann_event_source_news_detail -->  sf_secu_announcement_detail 表 
    dc_ann_event_source_ann_detail --> 

    dc_ann_event_source_ann_detail --> sf_secu_announcement_summary 表 

    dc_ann_event_source_ann_detail -> sf_const_announcement 表
