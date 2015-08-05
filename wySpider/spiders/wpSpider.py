#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: xiaoL-pkav l@pker.in
@version: 2015/8/6 0:33
"""

import scrapy


class WooyunSpider(scrapy.Spider):
    name = "wooyun"
    allowed_domains = ["wooyun.org"]
    start_urls = ["http://wooyun.org/bugs/new_public/page/1",
                  "http://wooyun.org/bugs/new_public/page/2"]

    def parse(self, response):
        filename = response.url.split("/")[-1]
        with open(filename, 'wb') as file:
            file.write(response.body)