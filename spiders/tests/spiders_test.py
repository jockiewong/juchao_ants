import datetime

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
_now = datetime.datetime.now()
_start = datetime.datetime(_now.year - 3, _now.month, _now.day)
finance_his.start(start_date=_start)
