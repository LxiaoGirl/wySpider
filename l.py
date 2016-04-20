#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: xiaoL-pkav l@pker.in
@version: 2015/10/10 16:02
"""

# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
from multiprocessing import Pool
import HTMLParser
from time import sleep
from os import makedirs
from random import randint


from lxml import etree

from libs.http import http_request_get

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.LBugs import LBugs
from db.LDetails import LDetails

from common.config import db_name, db_host, db_lib, db_port, db_pwd, db_type, db_user
from common.common import L_IMG_URL, WOOYUN_IMG_URL, L_IMG_PATH, WOOYUN_URL, L_IMG_PATH_OLD
from common.logger import L_LOGGER


def init_db():
    connect = "%s+%s://%s:%s@%s:%s/%s?charset=utf8" % (db_type, db_lib, db_user, db_pwd, db_host, db_port, db_name)
    engine = create_engine(connect)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


def get_bugs_url():
    session = init_db()
    base_number = 1
    base_url = 'https://www.wooyun.org/bugs/page/'
    repeat_flag = False
    sleep_time = 60
    while True:
        if repeat_flag:
            L_LOGGER.info(u"漏洞获取轮询结束，休眠60分钟")
            base_number = 1
            repeat_flag = False
            sleep(3600)
        target_url = "%s%s" % (base_url, base_number)
        L_LOGGER.info(u"获取目标 %s 页面漏洞列表。" % target_url)
        content = http_request_get(url=target_url)
        if content:
            sleep_time = 60
            html = content.text
            dom = etree.HTML(html)
            urls = dom.xpath("/html/body/div[5]/table[3]/tbody")
            # /html/body/div[5]/table[3]/tbody/tr[1]/td/a

            for url in urls:
                if not len(url):
                    repeat_flag = True
                    break
                for u in url:
                    bug_name = u[1][0].text
                    if not bug_name:
                        bug_name = u"邮件保护需重新爬取"
                    bug_url = "%s%s" % ("http://www.wooyun.org", u[1][0].get('href'))
                    is_exist = session.query(LBugs).filter(LBugs.BugUrl == bug_url).filter(LBugs.BugName == bug_name)\
                        .count()
                    if not is_exist:
                        new_bug_url = LBugs(BugUrl=bug_url, BugName=bug_name, IsGet=0)
                        session.add(new_bug_url)
                        session.commit()
            else:
                sleep(randint(0, 5))
                base_number += 1
                continue
        else:
            sleep(sleep_time)
            sleep_time += 60
            L_LOGGER.error(u"页面无法访问 %s！休眠 %s 秒！" % (target_url, sleep_time))
            #base_number += 1
    L_LOGGER.error(u"进程退出")
    session.close()


def get_bugs_details():
   # sleep(60)
    session = init_db()
    while True:
        bugs = session.query(LBugs).filter(LBugs.IsGet == 0).limit(100).all()
        if not bugs:
            session.query(LBugs).filter(LBugs.IsGet == 2).update({"IsGet": '0'})
            session.commit()
            L_LOGGER.info(u"详情轮询结束，休眠60分钟")
            sleep(3600*5)

        for bug in bugs:
            # 目标URL
            target_url = bug.BugUrl
            # 获取详情
            content = http_request_get(url=target_url)
            L_LOGGER.info(u"获取目标 %s 页面详情。" % target_url)

            if content:
                if is_404(content.text, target_url):
                    if is_open(content.text, target_url):
                        html = content.text
                        dom = etree.HTML(html)

                        bug_number = dom.xpath('//*[@id="bugDetail"]/div[5]/h3[1]/a')[0].text.strip()
                        bug_title = dom.xpath('//h3[@class="wybug_title"]')[0].text[7:].strip()
                        bug_company = dom.xpath('//*[@id="bugDetail"]/div[5]/h3[3]/a')[0].text[16:].strip()
                        bug_author = dom.xpath('//*[@id="bugDetail"]/div[5]/h3[4]/a')[0].text.strip()
                        bug_submit_time = dom.xpath('//h3[@class="wybug_date"]')[0].text[7:].strip()
                        bug_open_time = dom.xpath('//h3[@class="wybug_open_date"]')[0].text[7:].strip()
                        bug_type = dom.xpath('//h3[@class="wybug_type"]')[0].text[7:].strip()
                        bug_level = dom.xpath('//h3[@class="wybug_level"]')[0].text[7:].strip()
                        bug_describe = dom.xpath('//*[@id="bugDetail"]/div[5]/p[3]')[0].text
                        bug_state = dom.xpath('//*[@id="bugDetail"]/div[5]/div[1]')[0]
                        bug_state = HTMLParser.HTMLParser().unescape(etree.tostring(bug_state))
                        bug_state = download_img(bug_state)
                        bug_prove = dom.xpath('//*[@id="bugDetail"]/div[5]/div[2]')[0]
                        bug_prove = HTMLParser.HTMLParser().unescape(etree.tostring(bug_prove))

                        bug_prove = download_img(bug_prove)
                        bug_patch = dom.xpath('//*[@id="bugDetail"]/div[5]/div[3]/p')[0].text
                        attention = dom.xpath('//*[@id="attention_num"]')[0].text
                        collect = dom.xpath('//*[@id="collection_num"]')[0].text
                        reply_type = dom.xpath('//*[@id="bugDetail"]/div[5]/div[4]/p[1]')[0].text[5:].strip()

                        reply_rank = 0

                        if reply_type == u'无影响厂商忽略':
                            reply_time = dom.xpath('//*[@id="bugDetail"]/div[5]/div[4]/p[2]')[0].text[5:]
                            reply_details = dom.xpath('//*[@id="bugDetail"]/div[5]/div[4]/p[3]')[0].text
                            reply_new = dom.xpath('//*[@id="bugDetail"]/div[5]/div[4]/p[4]')[0].text

                        elif reply_type == u'厂商或者厂商积极拒绝':
                            reply_rank = 0
                            reply_time = None
                            reply_details = ''
                            reply_new = ''
                        else:
                            reply_rank = dom.xpath('//*[@id="bugDetail"]/div[5]/div[4]/p[2]')[0].text[7:]
                            reply_time = dom.xpath('//*[@id="bugDetail"]/div[5]/div[4]/p[3]')[0].text[5:]
                            reply_details = dom.xpath('//*[@id="bugDetail"]/div[5]/div[4]/p[4]')[0].text
                            reply_new = dom.xpath('//*[@id="bugDetail"]/div[5]/div[4]/p[5]')[0].text

                        new_bug_details = LDetails(Url=target_url, BugNumber=bug_number, BugTitle=bug_title,
                                                   BugCompany=bug_company, BugAuthor=bug_author, SubmitTime=bug_submit_time,
                                                   OpenTime=bug_open_time, BugType=bug_type, BugLevel=bug_level,
                                                   BugDescribe=bug_describe, BugState=bug_state, BugProve=bug_prove,
                                                   BugPatch=bug_patch, Attention=attention, Collect=collect,
                                                   ReplyType=reply_type, ReplyRank=reply_rank, ReplyTime=reply_time,
                                                   ReplyDetails=reply_details, ReplyNew=reply_new)
                        session.add(new_bug_details)
                        session.commit()
                        session.query(LBugs).filter(LBugs.Id == bug.Id).update({"IsGet": '1'})
                        session.commit()
                    else:
                        session.query(LBugs).filter(LBugs.Id == bug.Id).update({"IsGet": '2'})
                        session.commit()
                else:
                    session.query(LBugs).filter(LBugs.Id == bug.Id).update({"IsGet": '4'})
                    session.commit()
            # 随机休眠防止屏蔽
            sleep(randint(0, 5))

    session.close()


def is_open(html, target_url):
    dom = etree.HTML(html)
    bug_state = dom.xpath('//*[@id="bugDetail"]/div[5]/div[1]')[0]
    if bug_state.values() != ['wybug_detail']:
        L_LOGGER.warning(u"目标 %s 暂未公开详情。" % target_url)
        return False
    else:
        return True


def is_404(html, target_url):
    dom = etree.HTML(html)
    bug_404 = dom.xpath('//div[@class="error-404-number"]')
    if bug_404:
        L_LOGGER.warning(u"目标 %s 404已被删除。" % target_url)
        return False
    else:
        return True


def download_img(html):
    dom = etree.HTML(html)
    images = dom.xpath('//img')
    for image in images:
        src = image.get('src')
        if not src:
            continue
        if src.find('/') == 0:
            src = "%s%s" % (WOOYUN_URL, src[1:])
        url = src
        image_data = http_request_get(src, stream=True)
        if image_data:
            if src.find(WOOYUN_IMG_URL) == -1 and src.find(WOOYUN_IMG_URL) == -1:
                continue
            if src.find(WOOYUN_IMG_URL) == -1:
                l_img_src = src.replace(WOOYUN_URL, L_IMG_URL)
                down_img_path = url.replace(WOOYUN_URL, "")
                img_dir, img_path = url.replace(WOOYUN_URL, "").replace(L_IMG_PATH_OLD, "").split("/")
                try:
                    makedirs(L_IMG_PATH_OLD+img_dir)
                except OSError, e:
                    pass
            else:
                l_img_src = src.replace(WOOYUN_IMG_URL, L_IMG_URL)
                down_img_path = url.replace(WOOYUN_IMG_URL, "")
                img_dir, img_path = url.replace(WOOYUN_IMG_URL, "").replace(L_IMG_PATH, "").split("/")
                try:
                    makedirs(L_IMG_PATH+img_dir)
                except OSError, e:
                    pass
            img_file = open(down_img_path, "wb")
            for chunk in image_data.iter_content():
                img_file.write(chunk)
            img_file.close()
            L_LOGGER.info(u"图片 %s 下载成功。" % url)
            html = html.replace(src, l_img_src)

        # 随机休眠防止屏蔽
        sleep(randint(0, 5))
    return html


def program_init(path):
    # 初始化图片目录
    try:
        makedirs(path)
        L_LOGGER.info(u"图片目录建立成功。")
    except OSError, e:
        L_LOGGER.error(u"%s图片目录已经存在。%s" % (path, e))


def main():
    program_init(L_IMG_PATH)
    process_pool = Pool(2)
    process_pool.apply_async(get_bugs_url, args=())
    process_pool.apply_async(get_bugs_details(), args=())
    process_pool.close()
    process_pool.join()


def ip():
    import socket
    import struct
    session = init_db()
    from db.ips import ips
    fp = open('ip.txt')
    #(ip_string)
    for ip in fp.readlines():
        data = ip.split(' ')

        #print data[1].strip()
        #print struct.unpack("=I", socket.inet_aton(data[1].strip()))[0]
        new_bug_url = ips(startip=struct.unpack("=I", socket.inet_aton(data[0].strip()))[0], endip=struct.unpack("=I", socket.inet_aton(data[1].strip()))[0], location=data[2],details=data[3])
        session.add(new_bug_url)
        session.commit()


if __name__ == '__main__':
    main()
    #ip()