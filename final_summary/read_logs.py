import datetime

start_time = datetime.datetime(2019, 10, 1)
end_time = datetime.datetime(2020, 11, 6)


dt_list = []
dt = start_time
while dt <= end_time:
    dt_list.append(dt)
    dt += datetime.timedelta(days=1)


dt_str_list = [dt.strftime('%Y-%m-%d') for dt in dt_list]
# print(dt_str_list)

with open("final_1.log", 'r') as f:
    datas = f.readlines()
    datas = [data[:10] for data in datas]
    last_dts = sorted(list(set(dt_str_list) - set(datas)))

for ldt in last_dts:
    print(ldt)

print(len(last_dts))
