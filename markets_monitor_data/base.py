#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created  on 2015/1/14
import requests
import re
import json
import MySQLdb
import MySQLdb.cursors
from settings import *

import logging
from logging.handlers import RotatingFileHandler
import os

'''
相关文档
https://github.com/wallstreetcn/crawler/wiki/crawler-description
https://github.com/wallstreetcn/finance/wiki
'''

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

logFile = '%s//markets.log' % os.path.split(os.path.realpath(__file__))[0]

my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=500 * 1024 * 1024,
                                 backupCount=5, encoding=None, delay=True)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

app_log = logging.getLogger('')
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)

headers = {
    'Connection': 'keep-alive',
    'Accept': 'text/plain, */*; q=0.01',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 UBrowser/3.1.1644.34 Safari/537.36',
    'Referer': 'http://www.investing.com/',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
}

conn = MySQLdb.connect(
    host=MYSQL_HOST,
    db=MYSQL_DBNAME,
    user=MYSQL_USER,
    passwd=MYSQL_PASSWD,
    charset='utf8',
    use_unicode=True,
    port=MYSQL_PORT,
    cursorclass=MySQLdb.cursors.DictCursor)

conn.ping(True)
conn.autocommit(1)
cur = conn.cursor()


def re_get(regex, string):
    p = regex.search(string)
    if p:
        return p.group(1)
    else:
        return ''


def convert(string):
    string = string.replace(',', '').replace('+', '').strip()
    try:
        string = float(string)
    except:
        return 0
    else:
        return string


investing_last_price_re = re.compile(r'id="last_last">(.*?)</span>')


def get_investing(url):
    last_price = 0
    url = url.replace('http://www', 'http://jp')
    try:
        r = requests.get(url, headers=headers, timeout=10)
        content = r.content
        last_price = convert(re_get(investing_last_price_re, content))
    except Exception as e:
        app_log.error(str(e))

    return last_price


def get_cnbc(url):
    last_price = 0
    try:
        r = requests.get(url, headers=headers, timeout=10)
        json_data = json.loads(r.content)
        QuickQuote = json_data['QuickQuoteResult']['QuickQuote']
        last_price = float(QuickQuote['last'])
    except Exception as e:
        app_log.error(str(e))

    return last_price


def get_wallstreetcn(url):
    last_price = 0
    site_ctime = 0
    try:
        r = requests.get(url, headers=headers, timeout=3)
        json_data = json.loads(r.content)
        last_price = json_data['results'][0]['price']
        site_ctime = json_data['results'][0]['ctime']
    except Exception as e:
        app_log.error(str(e))
    return last_price, site_ctime


def get_gtimg(url):
    last_price = 0
    try:
        r = requests.get(url, headers=headers, timeout=10)
        last_price = r.content.split('~')[3]
        last_price = float(last_price)
    except Exception as e:
        app_log.error(str(e))

    return last_price


def get_data(url):
    last_price = 0
    url = url.strip()
    if 'investing.com' in url:
        last_price = get_investing(url)
    elif 'cnbc.com' in url:
        last_price = get_cnbc(url)
    elif 'wallstreetcn.com' in url:
        last_price, site_ctime = get_wallstreetcn(url)
    elif 'gtimg.cn' in url:
        last_price = get_gtimg(url)

    return last_price

