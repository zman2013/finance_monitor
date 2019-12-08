import datetime
import json
import time

from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request
from stock_index import index_service

bp = Blueprint('stock_index', __name__, url_prefix='/stock/index')


@bp.route('/view')
def view():
    return render_template("stock_index/view.html")


@bp.route('/json')
def index_analyse_chart():
    this_year = int(time.strftime("%Y"))
    start_year = str(this_year - 3)
    start_date = start_year + '0101'
    [buy_date, buy_index, sell_date, sell_index, sh_index_df, sz_index_df] = index_service.analyse_index(start_date)

    sh_index_df.set_index(sh_index_df['trade_date'], inplace=True)
    sh_index_df = sh_index_df[['close']]
    sh_index_df = sh_index_df.transpose()
    sh_index_df = sh_index_df.sort_index(axis=1, ascending=False)

    sz_index_df.set_index(sz_index_df['trade_date'], inplace=True)
    sz_index_df = sz_index_df[['close']]
    sz_index_df = sz_index_df.transpose()
    sz_index_df = sz_index_df.sort_index(axis=1, ascending=False)

    jsonData = {'sh_index_history': {},
                'sz_index_history':{},
                'buy_point':{},
                'sell_point': {}}
    jsonData['sh_index_history']['dates'] = sh_index_df.columns.values.tolist()
    jsonData['sh_index_history']['data'] = []
    jsonData['sz_index_history']['data'] = []
    jsonData['buy_point']['data'] = []
    jsonData['sell_point']['data'] = []

    # 上证指数
    data = json.loads(sh_index_df.to_json(orient="values"))
    for d in data:
        tmp = {}
        tmp['name'] = '上证'
        tmp['data'] = d
        tmp['type'] = 'line'
        jsonData['sh_index_history']['data'].append( tmp )

    # 深成指数
    data = json.loads(sz_index_df.to_json(orient="values"))
    for d in data:
        tmp = {}
        tmp['name'] = '深成'
        tmp['data'] = d
        tmp['type'] = 'line'
        tmp['yAxisIndex'] = 1
        jsonData['sz_index_history']['data'].append(tmp)

    # 画点（买入、卖出）
    tmp = {}
    tmp['name'] = '买入'
    tmp['data'] = []
    for i in range(0, len(buy_date)):
        tmp['data'].append([str(buy_date[i]), buy_index[i]])
    tmp['type'] = 'scatter'
    tmp['itemStyle'] = {'normal': {'color': '#f00'}}
    tmp['symbolSize'] = 10
    jsonData['buy_point']['data'].append(tmp)
    # 画点（买入、卖出）
    tmp = {}
    tmp['name'] = '卖出'
    tmp['data'] = []
    for i in range(0, len(sell_date)):
        tmp['data'].append([str(sell_date[i]), sell_index[i]])
    tmp['type'] = 'scatter'
    tmp['itemStyle'] = {'normal': {'color': '#080'}}
    tmp['symbolSize'] = 10
    jsonData['sell_point']['data'].append(tmp)

    return jsonify(jsonData)


@bp.route('/download')
def download():
    start_date = request.args.get('start_date')
    # 如果没有参数，获取最近一个月的数据
    if start_date is None or start_date == '':
        day_delta = datetime.timedelta(days=-30)

        today = datetime.datetime.today().date()

        start_date = today + day_delta
        start_date = start_date.strftime('%Y%m%d')

        print("start_date is null or empty, set start_date = ", start_date)

    index_service.download_sh_index(start_date=start_date)
    index_service.download_sz_index(start_date=start_date)

    json_data = {
        'data': 'success'
    }
    return jsonify(json_data)
