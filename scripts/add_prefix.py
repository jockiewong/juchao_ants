# 20201026 将中间表和软件表的股票代码加上前缀
# UPDATE announcement_base SET SecuCode=CONCAT('SH',SecuCode) WHERE SecuCode LIKE "6%";
# UPDATE announcement_base SET SecuCode=CONCAT('SZ',SecuCode) WHERE SecuCode LIKE "3%";
# UPDATE announcement_base SET SecuCode=CONCAT('SZ',SecuCode) WHERE SecuCode LIKE "0%";

# 分段 update
# max_id = 'select max(id) from announcement_base; '
# for start in range(max_id//100000 + 1):
#     sql = 'update xxx set where id >= {} and id <= {}...'.format(start, start*10000)

from base_spider import SpiderBase


class PrefixAdder(SpiderBase):
    def __init__(self):
        super(PrefixAdder, self).__init__()
        self.batch_num = 10000   # 单次更新的个数 不超过 10 M？

    def get_table_max_id(self, table_name: str):
        self._tonglian_init()
        sql = '''select max(id) as max_id from {}; '''.format(table_name)
        max_id = self.tonglian_client.select_one(sql).get("max_id")
        return max_id

    def launch(self):
        max_id = self.get_table_max_id("announcement_base")
        for start in range(max_id//self.batch_num + 1):
            print(start*self.batch_num, (start+1)*self.batch_num)




        pass


if __name__ == '__main__':
    PrefixAdder().launch()
