# -*- coding: utf-8 -*-

MYSQL_HOST = '127.0.0.1'
MYSQL_DBNAME = 'bhfxquote'
MYSQL_USER = 'root'
MYSQL_PASSWD = 'root'
MYSQL_PORT=3306

#允许的秒数误差，最后会与当前时间比较，得出绝对值，小于此值则认为是对的，forex_diff_seconds为外汇的，index_diff_seconds为指数的（这个要设大一点，因为许多指数都有延迟）
forex_diff_seconds=300
index_diff_seconds=1800
#最近更新时间在一分钟之内占整个外汇资产中的比率，比如85%，用小数表示为0.85，forex_raito为外汇比率，index_raito为指数比率

forex_raito=0.8
index_raito=0.2