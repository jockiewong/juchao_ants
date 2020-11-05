with open("final_1.log", 'r') as f:
    datas = f.readlines()
    datas = [data[:10] for data in datas]
    for data in sorted(datas):
        print(data)
