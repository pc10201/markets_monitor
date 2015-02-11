# coding=utf-8
from flask import *
import MySQLdb
import MySQLdb.cursors
from settings import *
import time
import arrow
import requests
import re

app = Flask(__name__)

status_re = re.compile(ur'<b>(.*?)</b')
name_re = re.compile(ur'\.(.*?)\.(com|cn)')

'''
app.config.from_object(__name__)
app.debug = True
app.secret_key = 'my project'
'''


def diff_result(diff_raito, diff_seconds, data, source):
    all_count = len(data)
    good_count = 0
    for row in data:
        if abs(row['ctime'] - time.time()) < diff_seconds:
            good_count = good_count + 1

    good_ratio = good_count * 1.0 / all_count
    item_list = []
    status = ''
    day_of_week, time_now = arrow.utcnow().to('local').format('d HH').split(' ')
    day_of_week = int(day_of_week)
    time_now = int(time_now)
    if day_of_week == 6 or day_of_week == 7 or (0 <= time_now <= 8):
        status = u'总的状态:Good!(可能休市中) 有效率:%.2f%% 允许误差时间:%d秒' % (good_ratio * 100, diff_seconds)

    is_good = good_ratio > diff_raito or 'Good' in status
    for row in data:
        if is_good:
            tr_class = 'warning'
        else:
            tr_class = 'danger'
        if abs(row['ctime'] - time.time()) < diff_seconds:
            tr_class = 'success'

        price_source = row['price_source']

        if 'money.netease' in price_source:
            price_source_name = u'网易财经'
        elif 'http' in price_source:
            price_source_name = name_re.search(price_source).group(1)
        else:
            price_source_name = price_source

        open_close_source = row['open_close_source'] or u'计算得出'

        if 'money.netease' in open_close_source:
            open_close_source_name = u'网易财经'
        elif 'http' in open_close_source:
            open_close_source_name = name_re.search(open_close_source).group(1)
        else:
            open_close_source_name = open_close_source
        title = row['subTitle'] or row['title']
        show_url = row['show_url']

        ctime = arrow.get(str(row['ctime']), 'X').to('local').format('YYYY-MM-DD HH:mm:ss')
        item_list.append(dict(
            title=title,
            tr_class=tr_class,
            show_url=show_url,
            price_source=price_source,
            open_close_source=open_close_source,
            price_source_name=price_source_name,
            open_close_source_name=open_close_source_name,
            ctime=ctime,
            spider_name=row['spider_name']
        ))

    if 'Good' in status:
        pass
    else:
        if good_ratio > diff_raito:
            status = u'总的状态:Good! 有效率:%.2f%% 允许误差时间:%d秒' % (good_ratio * 100, diff_seconds)
        else:
            status = u'总的状态:Bad! 有效率:%.2f%% 允许误差时间:%d秒' % (good_ratio * 100, diff_seconds)
            cur = g.db.cursor()
            cur.execute("insert into ax_monitor_log set symbol=%s,ctime=%s,record=%s,source=%s ", ("", int(time.time()), status, source))

    return item_list, status


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
    g.db.autocommit(True)
    g.db.ping(True)


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/forex', methods=['GET'])
def forex():
    cur = g.db.cursor()
    # cur.execute("select ax_newdata.symbol,ax_newdata.ctime,ax_finance.subTitle from ax_newdata,ax_finance WHERE ax_newdata.symbol=ax_finance.symbol and ax_finance.`status`='active' and ax_finance.`type`='forex' ORDER BY ax_newdata.ctime")
    sql = '''
select ax_config.symbol,ax_config.title,ax_config.subTitle,ax_config.show_url,ax_config.spider_name,
ax_config.price_source,ax_config.open_close_source,ax_config.diff_url,ax_newdata.ctime
from ax_config,ax_newdata
where ax_config.symbol=ax_newdata.symbol and ax_config.`status`='active'
and ax_config.`type`='forex'
ORDER BY ax_newdata.ctime
'''
    cur.execute(sql)
    data = cur.fetchall()
    item_list, status = diff_result(forex_raito, forex_diff_seconds, data, '外汇时间')

    return render_template('forex.html', item_list=item_list, status=status)


@app.route('/index', methods=['GET'])
def index():
    cur = g.db.cursor()
    # cur.execute("select ax_newdata.symbol,ax_newdata.ctime,ax_finance.subTitle from ax_newdata,ax_finance WHERE ax_newdata.symbol=ax_finance.symbol and ax_finance.`status`='active' and ax_finance.`type`='indice' ORDER BY ax_newdata.ctime")
    sql = '''
select ax_config.symbol,ax_config.title,ax_config.subTitle,ax_config.show_url,ax_config.spider_name,
ax_config.price_source,ax_config.open_close_source,ax_config.diff_url,ax_newdata.ctime
from ax_config,ax_newdata
where ax_config.symbol=ax_newdata.symbol and ax_config.`status`='active'
and (ax_config.`type`='cfdindice' or ax_config.`type`='indice')
ORDER BY ax_newdata.ctime
'''
    cur.execute(sql)
    data = cur.fetchall()
    item_list, status = diff_result(index_raito, index_diff_seconds, data, '指数时间')
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
    day_of_week, time_now = arrow.utcnow().to('local').format('d HH').split(' ')
    day_of_week = int(day_of_week)
    time_now = int(time_now)
    if day_of_week == 6 or day_of_week == 7 or (0 <= time_now <= 8):
        status = u'夜晚时间 代理状态:Good!'
    return render_template('proxy.html', status=status)


@app.route('/data', methods=['GET'])
def data():
    cur = g.db.cursor()

    cur.execute("select * from ax_config WHERE status='active' ORDER BY diff_status DESC ,importance DESC ")
    data = cur.fetchall()
    item_list = []
    status = u'总的状态:Good!'
    for row in data:
        price_source = row['price_source']

        if 'money.netease' in price_source:
            price_source_name = u'网易财经'
        elif 'http' in price_source:
            price_source_name = name_re.search(price_source).group(1)
        else:
            price_source_name = price_source

        open_close_source = row['open_close_source'] or u'计算得出'

        if 'money.netease' in open_close_source:
            open_close_source_name = u'网易财经'
        elif 'http' in open_close_source:
            open_close_source_name = name_re.search(open_close_source).group(1)
        else:
            open_close_source_name = open_close_source
        title = row['subTitle'] or row['title']
        show_url = row['show_url']
        diff_url = row['diff_url']
        if diff_url:
            diff_name = name_re.search(diff_url).group(1)
        else:
            diff_name = ''
        tr_class = 'success'

        if row['diff_status'] == 1:
            tr_class = 'danger'
            status = u'总的状态:Bad!'

        diff_price = row['diff_price']
        site_price = row['site_price']
        if row['ctime'] and row['site_ctime']:
            ctime = arrow.get(str(row['ctime']), 'X').to('local').format('YYYY-MM-DD HH:mm:ss')
            site_ctime = arrow.get(str(row['site_ctime']), 'X').to('local').format('YYYY-MM-DD HH:mm:ss')
        else:
            ctime = u'空值'
            site_ctime = u'空值'

        item_list.append(dict(
            title=title,
            tr_class=tr_class,
            show_url=show_url,
            price_source=price_source,
            open_close_source=open_close_source,
            price_source_name=price_source_name,
            open_close_source_name=open_close_source_name,
            diff_url=diff_url,
            diff_name=diff_name,
            diff_price=diff_price,
            site_price=site_price,
            ctime=ctime,
            site_ctime=site_ctime,
            diff_allow=row['diff_allow'],
            spider_name=row['spider_name']
        ))
    return render_template('data.html', item_list=item_list, status=status)


@app.route('/log', methods=['GET'])
def log():
    cur = g.db.cursor()
    cur.execute("select * from ax_monitor_log ORDER BY id DESC limit 100")
    data = cur.fetchall()
    item_list = []
    for row in data:
        tr_class = 'danger'

        item_list.append(dict(symbol=row['symbol'], record=row['record'], tr_class=tr_class, source=row['source'],
                              ctime=arrow.get(str(row['ctime']), 'X').to('local').format('YYYY-MM-DD HH:mm:ss')))
    return render_template('log.html', item_list=item_list)


@app.errorhandler(404)
def page_not_found(error):
    return 'page_not_found', 404


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9001, debug=True)
