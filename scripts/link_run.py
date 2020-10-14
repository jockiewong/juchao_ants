import requests


def get_redit_link():
    first_link = '''http://www.cninfo.com.cn/new/disclosure/detail?plate=szse&orgId=9900023797&stockCode=300424&announcementId=1208372407&announcementTime=2020-09-01%2019:28'''
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}
    resp = requests.get(first_link, headers=headers)
    redit_list = resp.history
    # redit_link = redit_list[0].headers["location"]
    redit_link = redit_list[len(redit_list)-1].headers["location"]
    print(redit_link)
    return redit_link


def if_final_link(link: str):
    if link.endswith("PDF"):
        return True
    else:
        return False


def link_null(record, dt):
    record = {'obRecid3907': 40446434, 'textId': 1207948410, 'classifiedId': '030402', 'code': '',
              'pageUrl': 'finalpage/2020-06-22/cninfo1207948410.js', 'title': '深市上市公司网络投票特别提示', 'fileType': 'TXT',
              'announcementTime': 1592786974000, 'entryTime': 1592786974000, 'pagePath': None, 'top': False, 'type': '通知'}
    # http://www.cninfo.com.cn/new/disclosure/detail?stock=&announcementId=1207948410&announcementTime=2020-06-22
    base_url = '''http://www.cninfo.com.cn/new/disclosure/detail?stock=&announcementId={}&announcementTime={}'''.format(record.get("textId"), dt)


def main():
    link1 = 'http://static.cninfo.com.cn/finalpage/2020-06-09/1207905896.PDF'
    link2 = 'http://www.cninfo.com.cn/new/disclosure/detail?stockCode=603707&announcementId=1207926163&orgId=9900022971&announcementTime=2020-06-16'
    print(if_final_link(link1))
    print(if_final_link(link2))


if __name__ == '__main__':
    main()
