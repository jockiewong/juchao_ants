'''
docker build -f Dockerfile -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_base:v1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_base:v1
sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_base:v1
'''


'''
sudo docker run --log-opt max-size=10m --log-opt max-file=3 \
-itd --name jclive --env LOCAL=1 --env VPN=1 \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_base:v1 \
python livenews/single_spider.py
'''


'''
sudo docker run --log-opt max-size=10m --log-opt max-file=3 \
-itd --name ant --env LOCAL=1 --env VPN=1 \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_base:v1 \
python history_ant/his_task.py
'''


''' 
sudo docker run --log-opt max-size=10m --log-opt max-file=3 \
-itd --name ant_merge --env LOCAL=1  --env VPN=1 \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_base:v1 \
python scripts/trans_2tl.py
'''

'''guba 
sudo docker run --log-opt max-size=10m --log-opt max-file=3 \
-itd --name test --env LOCAL=1  --env VPN=1 \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_base:v1 \
python api_tests/guba_gener_demo.py
'''

'''news 
sudo docker run --log-opt max-size=10m --log-opt max-file=3 \
-itd --name news --env LOCAL=1  --env VPN=1 \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_base:v1 \
python api_tests/news_gener_demo.py

'''
