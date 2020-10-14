import os
import sys
import time

import schedule

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from livenews.merge_spider import MergeJuchaoDayNews
from livenews.single_spider import SingleJuchaoDayNews


def task():
    # MergeJuchaoDayNews().run()
    SingleJuchaoDayNews().start()


def main():

    task()
    # schedule.every(30).seconds.do(task)
    #
    # while True:
    #     schedule.run_pending()
    #     time.sleep(10)


if __name__ == '__main__':
    main()



'''
cd ../ 
docker build -f Dockerfile_live -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_live:v1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_live:v1 
sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_live:v1 
sudo docker run --log-opt max-size=10m --log-opt max-file=3 \
-itd --name jclive --env LOCAL=0 registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao_live:v1
'''