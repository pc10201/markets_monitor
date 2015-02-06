# coding=utf-8
from flask import *
import MySQLdb
import MySQLdb.cursors
from settings import *
import time
import arrow
import requests


app = Flask(__name__)
'''
app.config.from_object(__name__)
app.debug = True
app.secret_key = 'my project'
'''

@app.before_request
def before_request():
    g.db = MySQLdb.connect(
        host=MYSQL_HOST,
        db=MYSQL_DBNAME,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWD,
        charset='utf8',
        use_unicode=True,
        port=MYSQL_PORT,
        cursorclass=MySQLdb.cursors.DictCursor
    )


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/', methods=['GET', 'POST'])
def home():
    return u'index'


@app.route('/forex', methods=['GET'])
def forex():
    cur = g.db.cursor()
    cur.execute("select ax_newdata.symbol,ax_newdata.ctime,ax_finance.subTitle from ax_newdata,ax_finance WHERE ax_newdata.symbol=ax_finance.symbol and ax_finance.`status`='active' and ax_finance.`type`='forex' ORDER BY ax_newdata.ctime")
    data = cur.fetchall()
    all_count = len(data)
    item_list = []
    good_count = 0
    diff_seconds = forex_diff_seconds
    for row in data:
        tr_class = 'danger'
        if abs(row['ctime'] - time.time()) < diff_seconds:
            tr_class = 'success'
            good_count = good_count + 1

        item_list.append(dict(symbol=row['symbol'], subTitle=row['subTitle'], tr_class=tr_class, ctime=arrow.get(str(row['ctime']), 'X').format('YYYY-MM-DD HH:mm:ss')))
    good_ratio = good_count * 1.0 / all_count
    if good_count * 1.0 / all_count > forex_raito:
        status = u'总的状态:Good! 有效率:%.2f%% 允许误差时间:%d秒' % (good_ratio * 100, diff_seconds)
    else:
        status = u'总的状态:Bad! 有效率:%.2f%% 允许误差时间:%d秒' % (good_ratio * 100, diff_seconds)
    day_of_week, time_now = arrow.utcnow().replace(hours=8).format('d HHmmss').split(' ')
    day_of_week = int(day_of_week)
    time_now = int(time_now)
    if day_of_week == 6 or day_of_week == 7 or (0 <= time_now <= 80000):
        status = '总的状态:Good!(可能休市中) 有效率:%.2f%% 允许误差时间:%d秒' % (good_ratio * 100, diff_seconds)
    return render_template('forex.html', item_list=item_list, status=status)


@app.route('/index', methods=['GET'])
def index():
    cur = g.db.cursor()
    # cur.execute("select ax_newdata.symbol,ax_newdata.ctime,ax_finance.subTitle from ax_newdata,ax_finance WHERE ax_newdata.symbol=ax_finance.symbol and ax_finance.`status`='active' and ax_finance.`type`='indice' ORDER BY ax_newdata.ctime")
    cur.execute("select ax_newdata.symbol,ax_newdata.ctime,ax_finance.subTitle from ax_newdata,ax_finance WHERE ax_newdata.symbol=ax_finance.symbol and ax_finance.`status`='active' and (ax_finance.`type`='cfdindice' or ax_finance.`type`='indice') ORDER BY ax_newdata.ctime")
    data = cur.fetchall()
    all_count = len(data)
    item_list = []
    good_count = 0
    diff_seconds = index_diff_seconds
    for row in data:
        tr_class = 'danger'
        if abs(row['ctime'] - time.time()) < diff_seconds:
            tr_class = 'success'
            good_count = good_count + 1

        item_list.append(dict(symbol=row['symbol'], subTitle=row['subTitle'], tr_class=tr_class, ctime=arrow.get(str(row['ctime']), 'X').format('YYYY-MM-DD HH:mm:ss')))
    good_ratio = good_count * 1.0 / all_count
    if good_count * 1.0 / all_count > index_raito:
        status = u'总的状态:Good! 有效率:%.2f%% 允许误差时间:%d秒' % (good_ratio * 100, diff_seconds)
    else:
        status = u'总的状态:Bad! 有效率:%.2f%% 允许误差时间:%d秒' % (good_ratio * 100, diff_seconds)
    day_of_week, time_now = arrow.utcnow().replace(hours=8).format('d HHmmss').split(' ')
    day_of_week = int(day_of_week)
    time_now = int(time_now)
    if day_of_week == 6 or day_of_week == 7 or (time_now >= 0 and time_now < 80000):
        status = u'总的状态:Good!(可能休市中) 有效率:%.2f%% 允许误差时间:%d秒' % (good_ratio * 100, diff_seconds)
    return render_template('index.html', item_list=item_list, status=status)


@app.route('/proxy', methods=['GET'])
def proxy():
    proxies = {
        "http": "http://127.0.0.1:1984",
    }
    status = ''
    try:
        r = requests.get('http://baidu.com', proxies=proxies, timeout=1)
        if 'baidu.com' in r.content:
            status = u'代理状态:Good! '
    except Exception as e:
        status = u'代理状态:Bad! 错误:%s' % (str(e))
    day_of_week, time_now = arrow.utcnow().replace(hours=8).format('d HHmmss').split(' ')
    day_of_week = int(day_of_week)
    time_now = int(time_now)
    if day_of_week == 6 or day_of_week == 7 or (0 <= time_now <= 80000):
        status = u'夜晚时间 代理状态:Good!'
    return render_template('proxy.html', status=status)


@app.errorhandler(404)
def page_not_found(error):
    return 'page_not_found', 404


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9001, debug=True)
