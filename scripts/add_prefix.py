# 20201026 将中间表和软件表的股票代码加上前缀
# UPDATE announcement_base SET SecuCode=CONCAT('SH',SecuCode) WHERE SecuCode LIKE "6%";
# UPDATE announcement_base SET SecuCode=CONCAT('SZ',SecuCode) WHERE SecuCode LIKE "3%";
# UPDATE announcement_base SET SecuCode=CONCAT('SZ',SecuCode) WHERE SecuCode LIKE "0%";

# 分段 update
# max_id = 'select max(id) from announcement_base; '
# for start in range(max_id//100000 + 1):
#     sql = 'update xxx set where id >= {} and id <= {}...'.format(start, start*10000)
import sys

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

        self._tonglian_init()
        for start in range(max_id//self.batch_num + 1):
            _start, _end = start*self.batch_num, (start+1)*self.batch_num
            sh_update_sql = '''UPDATE announcement_base SET SecuCode=CONCAT('SH',SecuCode) \
WHERE id >= {} and id <= {} and SecuCode LIKE "6%"; '''.format(_start, _end)
            sh_update_count = self.tonglian_client.insert(sh_update_sql)

            sz_update_sql = '''UPDATE announcement_base SET SecuCode=CONCAT('SZ',SecuCode)\
WHERE id >= {} and id <= {} and SecuCode LIKE "3%"; '''.format(_start, _end)
            sz_update_count = self.tonglian_client.insert(sz_update_sql)

            sz_update_sql2 = '''UPDATE announcement_base SET SecuCode=CONCAT('SZ',SecuCode)\
WHERE id >= {} and id <= {} and SecuCode LIKE "0%"; '''.format(_start, _end)
            sz_update_count2 = self.tonglian_client.insert(sz_update_sql2)

            print("sh: {}\tsz_3: {}\tsz_0:{}".format(sh_update_count, sz_update_count, sz_update_count2))


if __name__ == '__main__':
    PrefixAdder().launch()
