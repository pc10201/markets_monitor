#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created  on 2015/1/14
from base import *
import time

cur.execute("select * from ax_config WHERE importance=5 and diff_url!='' ")

data = cur.fetchall()

while 1:
# for i in xrange(1):
    for item in data:
        diff_url = item['diff_url']
        diff_allow = item['diff_allow']
        site_url = 'http://api.markets.wallstreetcn.com/v1/price.json?symbol=%s' % item['symbol']

        try:
            diff_price = get_data(diff_url)
            site_price, site_ctime = get_wallstreetcn(site_url)
            ctime = int(time.time())
            if diff_price and site_price:
                if abs(diff_price - site_price) > diff_allow:
                    cur.execute("insert into log set symbol=%s,diff_price=%s,site_price=%s,ctime=%s,site_ctime=%s", (item['symbol'], diff_price, site_price, ctime, site_ctime))
                    cur.execute("update ax_config set diff_price=%s,site_price=%s,ctime=%s,site_ctime=%s,diff_status=1 WHERE id=%s", (diff_price, site_price, ctime, site_ctime, item['id']))
                else:
                    cur.execute("update ax_config set diff_price=%s,site_price=%s,ctime=%s,site_ctime=%s,diff_status=0 WHERE id=%s", (diff_price, site_price, ctime, site_ctime, item['id']))
        except Exception as e:
            app_log.error(str(e))
            continue