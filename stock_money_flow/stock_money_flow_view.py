import json

from flask import Blueprint
from flask import jsonify
from flask import render_template
from stock_money_flow import stock_money_flow_service

bp = Blueprint('stock_money_flow', __name__, url_prefix='/stock/money/flow')


@bp.route('/view')
def view():
    return render_template("stock_money_flow/view.html")


@bp.route('/json')
def info():
    df = stock_money_flow_service.load_money_flow_weekly_df()

    df.set_index(df['trade_date'], inplace=True)

    jsonData = {'index': {}, 'money_flow_pure':{}}
    jsonData['index']['data'] = []
    jsonData['money_flow_pure']['data'] = []

    # 格式化指数数据
    index_df = df[['close']]
    index_df = index_df.transpose()
    index_df = index_df.sort_index(axis=1, ascending=False)

    jsonData['index']['dates'] = index_df.columns.values.tolist()

    data = json.loads(index_df.to_json(orient="values"))
    for d in data:
        tmp = {}
        tmp['name'] = '上证指数'
        tmp['data'] = d
        tmp['type'] = 'line'

        jsonData['index']['data'].append(tmp)

    # 格式化资金流向数据
    money_df = df[['delta']]
    money_df = money_df.transpose()
    money_df = money_df.sort_index(axis=1, ascending=False)

    data = json.loads(money_df.to_json(orient="values"))
    for d in data:
        tmp = {}
        tmp['name'] = '资金净流向'
        tmp['data'] = d
        tmp['type'] = 'line'
        tmp['yAxisIndex'] = 1
        jsonData['money_flow_pure']['data'].append(tmp)

    return jsonify(jsonData)


@bp.route('/download')
def download():
    result = stock_money_flow_service.download()
    json_data = {
        'data': result
    }
    return jsonify(json_data)
