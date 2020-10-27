# 20201026 将中间表和软件表的股票代码加上前缀
# UPDATE announcement_base SET SecuCode=CONCAT('SH',SecuCode) WHERE SecuCode LIKE "6%";
# UPDATE announcement_base SET SecuCode=CONCAT('SZ',SecuCode) WHERE SecuCode LIKE "3%";
# UPDATE announcement_base SET SecuCode=CONCAT('SZ',SecuCode) WHERE SecuCode LIKE "0%";

# 分段 update
# max_id = 'select max(id) from announcement_base; '
# for start in range(max_id//100000 + 1):
#     sql = 'update xxx set where id >= {} and id <= {}...'.format(start, start*10000)
