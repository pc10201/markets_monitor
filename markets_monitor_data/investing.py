#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created  on 2015/2/6

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created  on 2015/1/14
from base import *
import time
import math

cur.execute("select * from ax_config WHERE status='active' and diff_url like '%investing%' ")

data=cur.fetchall()

start_time=time.time()
#while 1:
for i in xrange(1):
    for item in data:
        diff_url=item['diff_url']
        #pow_format=item['pow_format']
        diff_allow=item['diff_allow']
        site_url='http://api.markets.wallstreetcn.com/v1/price.json?symbol=%s' %item['symbol']
        try:
            diff_price=get_data(diff_url)

            ctime=int(time.time())

            site_price,site_ctime=get_wallstreetcn(site_url)

            if diff_price and site_price:
                #print item['symbol'],diff_price,site_price,pow_format,diff_allow
                #print u'允许误差',diff_allow*1.0/math.pow(10,pow_format)
                if abs(diff_price-site_price)>diff_allow:
                    print diff_url,diff_allow
                    cur.execute("insert into log set symbol=%s,diff_price=%s,site_price=%s,ctime=%s,site_ctime=%s",(item['symbol'],diff_price,site_price,ctime,site_ctime))
                    cur.execute("update ax_config set diff_price=%s,site_price=%s,ctime=%s,site_ctime=%s,diff_status=1 WHERE id=%s",(diff_price,site_price,ctime,site_ctime,item['id']))
                else:
                    cur.execute("update ax_config set diff_price=%s,site_price=%s,ctime=%s,site_ctime=%s,diff_status=0 WHERE id=%s",(diff_price,site_price,ctime,site_ctime,item['id']))
        except Exception as e:
            app_log.error(str(e))

end_time=time.time()
print end_time-start_time