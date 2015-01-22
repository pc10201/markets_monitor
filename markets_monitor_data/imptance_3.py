#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created  on 2015/1/14
from base import *
import time

#非重要数据的外汇指数重要性是3

cur.execute("select * from ax_config WHERE importance=3 and `type`='forex' and diff_url!='' ")

data=cur.fetchall()

#while 1:
for i in xrange(1):
    for item in data:
        diff_price=get_data(item['diff_url'])
        site_url='http://api.markets.wallstreetcn.com/v1/price.json?symbol=%s' %item['symbol']
        get_data(site_url)
        ctime=int(time.time())
        if diff_price:
            cur.execute("update ax_config set diff_price =%s,ctime=%s WHERE id=%s",(diff_price,ctime,item['id']))