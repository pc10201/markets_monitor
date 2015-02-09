# coding=utf-8
from flask import *
import MySQLdb
import MySQLdb.cursors
from settings import *
import time
import arrow
import re
import requests

app = Flask(__name__)
'''
app.config.from_object(__name__)
app.debug = True
app.secret_key = 'my project'
'''

status_re = re.compile(ur'<b>(.*?)</b')
name_re = re.compile(ur'\.(.*?)\.(com|cn)')


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


@app.route('/', methods=['GET'])
def index():
    forex_status = u'获取最新状态失败，请手动点击链接进入'
    index_status = u'获取最新状态失败，请手动点击链接进入'
    try:
        r = requests.get('http://monitor.wallstreetcn.com/forex', timeout=2)
        forex_status = status_re.search(unicode(r.content, 'utf-8')).group(1)
        r = requests.get('http://monitor.wallstreetcn.com/index', timeout=2)
        index_status = status_re.search(unicode(r.content, 'utf-8')).group(1)
    except Exception as e:
        pass

    cur = g.db.cursor()
    ctime_diff = int(time.time()) - diff_seconds
    cur.execute("select symbol,count(id) as `count` from log WHERE ctime>%s GROUP BY symbol", (ctime_diff,))
    data = cur.fetchall()

    status = u'总的状态:All Good!'

    for item in data:
        if item['count'] > 3:
            status = u'总的状态:Bad!'
            continue
    ctime_diff = 0
    cur.execute("select * from ax_config WHERE status='active' ORDER BY diff_status DESC ,importance DESC ")
    data = cur.fetchall()
    item_list = []

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

        diff_price = row['diff_price']
        site_price = row['site_price']
        if row['ctime'] and row['site_ctime']:
            ctime = arrow.get(str(row['ctime']), 'X').replace(hours=8).format('YYYY-MM-DD HH:mm:ss')
            site_ctime = arrow.get(str(row['site_ctime']), 'X').replace(hours=8).format('YYYY-MM-DD HH:mm:ss')
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
    return render_template('index.html', item_list=item_list, status=status, forex_status=forex_status, index_status=index_status)


@app.route('/log', methods=['GET'])
def log():
    cur = g.db.cursor()
    cur.execute("select * from log ORDER BY id DESC limit 100")
    data = cur.fetchall()
    item_list = []
    for row in data:
        tr_class = 'danger'

        item_list.append(dict(symbol=row['symbol'], record=row['record'], tr_class=tr_class, ctime=arrow.get(str(row['ctime']), 'X').format('YYYY-MM-DD HH:mm:ss')))
    return render_template('log.html', item_list=item_list)


@app.route('/all', methods=['GET'])
def all():
    cur = g.db.cursor()
    cur.execute("select * from ax_config WHERE  status='active'")
    data = cur.fetchall()
    item_list = []
    for row in data:
        title = row['subTitle'] or row['title']
        show_url = row['show_url']
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

        diff_url = row['diff_url']
        if diff_url:
            diff_name = name_re.search(diff_url).group(1)
        else:
            diff_name = ''

        item_list.append(dict(
            title=title,
            show_url=show_url,
            price_source=price_source,
            open_close_source=open_close_source,
            price_source_name=price_source_name,
            open_close_source_name=open_close_source_name,
            diff_url=diff_url,
            diff_name=diff_name,
            diff_allow=row['diff_allow']
        ))
    return render_template('all.html', item_list=item_list)


@app.errorhandler(404)
def page_not_found(error):
    return 'page_not_found', 404


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9001, debug=True)
