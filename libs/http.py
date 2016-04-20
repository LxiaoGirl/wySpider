#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: xiaoL-pkav l@pker.in
@version: 2015/10/10 16:54
"""


import thirdparty.requests as requests
# 动态使用代理，为空不使用，支持用户密码认证
proxies = {
    # "http": "http://user:pass@10.10.1.10:3128/",
    # "https": "http://10.10.1.10:1080",
}

# 动态配置项
retry_cnt = 3  # 重试次数
timeout = 10  # 超时时间


def http_request_get(url, body_content_workflow=0,stream=False):
    trycnt = 0

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36',
        'Referer': url,
        'X-CSRF-Token': 'gq+Gnl4JMKKOhALUqNUwZmVBQvEPr7GwB83R26v4SRo=',
        'Cookie': 'Hm_lvt_c12f88b5c1cd041a732dea597a5ec94c=1445508519,1447835208; bdshare_firstime=1406012352921; __cfduid=d332bae9f4e8436979014dc2898aadb521427525951; PHPSESSID=grsutmbkjv942rgdvot3j8jd25; wy_uid=4a16IUdtWwwtFHCYfHaWUq1GsXLBZ7Nt7obf4Ww6q4Ry; wy_pwd=d437Bj2YxrEN8YXL7zLZ3%2FAwIHu00E1CdXktJy6K4421FwRmhRX%2BFVpqBDmgZ7jPV7RvIfZfodBrSEdYBA; wy_token=3dd1db3721a539c70e82f84e24407515; Hm_lpvt_c12f88b5c1cd041a732dea597a5ec94c=1447835243'}
    while True:
        try:
            if body_content_workflow == 1:
                result = requests.get(url, stream=True, headers=headers, timeout=timeout, proxies=proxies, verify=False)
                return result
            else:
                result = requests.get(url, headers=headers, timeout=timeout, proxies=proxies, verify=False)
                return result
        except Exception, e:
            # print 'Exception: %s' % e
            trycnt += 1
            if trycnt >= retry_cnt:
                # print 'retry overflow'
                return False
