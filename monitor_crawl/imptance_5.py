#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created  on 2015/1/14
from base import *
import time
import arrow

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
            site_ctime_human = arrow.get(str(site_ctime), 'X').to('local').format('YYYY-MM-DD HH:mm:ss')
            if diff_price and site_price:
                if abs(diff_price - site_price) * 1.0 / diff_price > diff_allow:
                    record = u'主站数据:%f（更新时间:%s），参照数据:%f' % (site_price, site_ctime_human, diff_price)
                    cur.execute("insert into ax_monitor_log set symbol=%s,ctime=%s,record=%s,source='数据监控'", (item['symbol'], ctime, record))
                    cur.execute("update ax_config set diff_price=%s,site_price=%s,ctime=%s,site_ctime=%s,diff_status=1 WHERE id=%s", (diff_price, site_price, ctime, site_ctime, item['id']))
                else:
                    cur.execute("update ax_config set diff_price=%s,site_price=%s,ctime=%s,site_ctime=%s,diff_status=0 WHERE id=%s", (diff_price, site_price, ctime, site_ctime, item['id']))
        except Exception as e:
            app_log.error(str(e))
            continue