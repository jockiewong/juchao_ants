from spiders.juchao_finance_hotfixes_spider import JuchaoFinanceSpider
from spiders.juchao_historyants_spider import JuchaoHistorySpider
from spiders.juchao_livenews_spider import JuchaoLiveNewsSpider

# jclive = JuchaoLiveNewsSpider()
# print(jclive.get_secu_abbr("990018"))
# jclive._create_table()
# jclive.start()

# jc_his = JuchaoHistorySpider()
# jc_his.start()

finance_his = JuchaoFinanceSpider()
finance_his.start()
