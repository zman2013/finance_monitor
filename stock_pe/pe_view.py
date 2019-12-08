import datetime
import json

from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request
from stock_pe import pe_analyzer
from stock_pe import pe_service

bp = Blueprint('index_pe', __name__, url_prefix='/stock/pe')


@bp.route('/view')
def view():
    return render_template("stock_pe/view.html")


@bp.route('/json')
def info():
    # 上证pe
    sh_pe_df = pe_service.load_sh_pe_df()

    sh_pe_df.set_index(sh_pe_df['searchDate'], inplace=True)
    pe_df = sh_pe_df
    sh_pe_df = sh_pe_df[['profitRate']]
    sh_pe_df = sh_pe_df.transpose()
    sh_pe_df = sh_pe_df.sort_index(axis=1, ascending=False)

    jsonData = {'sh_pe': {}}
    jsonData['sh_pe']['dates'] = sh_pe_df.columns.values.tolist()
    jsonData['sh_pe']['data'] = []

    data = json.loads(sh_pe_df.to_json(orient="values"))
    for d in data:
        tmp = {}
        tmp['name'] = '上证pe'
        tmp['data'] = d
        tmp['type'] = 'line'
        jsonData['sh_pe']['data'].append(tmp)

    # 深成pe
    sz_pe_df = pe_service.load_sz_pe_df()

    sz_pe_df.set_index(sz_pe_df['searchDate'], inplace=True)
    sz_pe_df = sz_pe_df[['profitRate']]
    sz_pe_df = sz_pe_df.transpose()
    sz_pe_df = sz_pe_df.sort_index(axis=1, ascending=False)

    jsonData['sz_pe'] = {}
    jsonData['sz_pe']['data'] = []

    data = json.loads(sz_pe_df.to_json(orient="values"))
    for d in data:
        tmp = {}
        tmp['name'] = '深成pe'
        tmp['data'] = d
        tmp['type'] = 'line'
        tmp['yAxisIndex'] = 1
        jsonData['sz_pe']['data'].append(tmp)

    # 获取警告点
    [buy_date, buy_index, sell_date, sell_index] = pe_analyzer.calculate_warning_point(pe_df)

    tmp = {}
    tmp['name'] = '买入'
    tmp['data'] = []
    for i in range(0, len(buy_date)):
        tmp['data'].append([str(buy_date[i]), buy_index[i]])
    tmp['type'] = 'scatter'
    tmp['itemStyle'] = {'normal': {'color': '#f00'}}
    tmp['symbolSize'] = 10
    jsonData['buy_point'] = {}
    jsonData['buy_point']['data'] = []
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
    jsonData['sell_point'] = {}
    jsonData['sell_point']['data'] = []
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

    pe_service.download_sh_pe(start_date=start_date)
    pe_service.download_sz_pe(start_date=start_date)
    json_data = {
        'data': 'success'
    }
    return jsonify(json_data)
