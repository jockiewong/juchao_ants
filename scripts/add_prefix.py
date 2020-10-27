# 20201026 将中间表和软件表的股票代码加上前缀
# UPDATE announcement_base SET SecuCode=CONCAT('SH',SecuCode) WHERE SecuCode LIKE "6%";
# UPDATE announcement_base SET SecuCode=CONCAT('SZ',SecuCode) WHERE SecuCode LIKE "3%";
# UPDATE announcement_base SET SecuCode=CONCAT('SZ',SecuCode) WHERE SecuCode LIKE "0%";

# 分段 update
# max_id = 'select max(id) from announcement_base; '
# for start in range(max_id//100000 + 1):
#     sql = 'update xxx set where id >= {} and id <= {}...'.format(start, start*10000)

# 以 0 1 2 3 6 9 开头的股票都有
# 20201027 确认需求只要 0 3 6 开头的 删除 1 2 9

import os
import sys
cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

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
        print("max id is {}".format(max_id))

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

            print("start: {}\t end: {}\t sh: {}\tsz_3: {}\tsz_0:{}".format(
                _start, _end, sh_update_count, sz_update_count, sz_update_count2))

# duck 不必
#             delete_sql = '''delete from announcement_base where \
# id >= {} and id <= {} and \
# (SecuCode like '1%' or SecuCode like '2%' or SecuCode like '9%'); '''.format(_start, _end)
#             delete_count = self.tonglian_client.delete(delete_sql)
#             print("delete {}".format(delete_count))

            self.tonglian_client.end()


if __name__ == '__main__':
    PrefixAdder().launch()
