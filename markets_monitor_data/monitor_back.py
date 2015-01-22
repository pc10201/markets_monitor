#coding=utf-8
import requests
import MySQLdb
import MySQLdb.cursors
import re
import arrow
import time
import json
import os
import logging
from logging.handlers import RotatingFileHandler
from settings import *
import math
'''
相关文档
https://github.com/wallstreetcn/crawler/wiki/crawler-description
https://github.com/wallstreetcn/finance/wiki
'''

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

logFile = '%s//markets.log' %os.path.split(os.path.realpath(__file__))[0]

my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=500*1024*1024,
                                 backupCount=5, encoding=None, delay=True)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

app_log = logging.getLogger('')
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)

headers={
'Connection': 'keep-alive',
'Accept': 'text/plain, */*; q=0.01',
'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 UBrowser/3.1.1644.34 Safari/537.36',
'Referer': 'http://www.investing.com/',
'Accept-Encoding': 'gzip,deflate,sdch',
'Accept-Language': 'zh-CN,zh;q=0.8',
}


filename='%s/monitorConfig.json' %(os.path.split(os.path.realpath(__file__))[0])
f=open(filename,'r')
resp=f.read()
f.close()

sleep_time=2
resp_json=json.loads(resp)

conn= MySQLdb.connect(
    host=MYSQL_HOST,
    db=MYSQL_DBNAME,
    user=MYSQL_USER,
    passwd=MYSQL_PASSWD,
    charset='utf8',
    use_unicode = True,
    port=MYSQL_PORT,
    cursorclass=MySQLdb.cursors.DictCursor)

conn.ping(True)
conn.autocommit(1)
cur= conn.cursor()


last_price_re=re.compile(r'id="last_last">(.*?)</span>')

def re_get(regex,string):
    p=regex.search(string)
    if p:
        return p.group(1)
    else:
        return ''

def convert(string):
    string=string.replace(',','').replace('+','').strip()
    try:
        string=float(string)
    except:
        return 0
    else:
        return string

s=requests.Session()
while 1:
    for k,v in resp_json.items():
        symbol= k
        url=v.get('url','').replace('http://www','http://jp')
        diff=v.get('diff','')
        pow_format=v.get('format',0)
        try:
            r=s.get(url,headers=headers,timeout=20)
            content=r.content
            if r.status_code!=200:
                continue
            last_price=convert(re_get(last_price_re,content))

            my_url='http://api.markets.wallstreetcn.com/v1/price.json?symbol=%s' %k

            r2=s.get(my_url,timeout=20)
            if r2.status_code!=200:
                continue
            my_last_price=r2.json()['results'][0]['price']

            record="symbol:%s source:%f wallstreetcn:%f" %(symbol,last_price,my_last_price)
            if abs(last_price-my_last_price)*math.pow(10,pow_format)>diff:
                ctime=int(time.time())
                cur.execute('insert into log set symbol=%s,ctime=%s,record=%s',(symbol,ctime,record))
                conn.commit()
                app_log.info(cur._last_executed)
            else:
                app_log.info(record)

        except Exception as e:
            app_log.error(str(e))
            continue

