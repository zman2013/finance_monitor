import json
import time

from flask import Blueprint, jsonify

from stock import stock_service

bp = Blueprint('stock', __name__, url_prefix='/stock')


# 个股pe信息
@bp.route('/pe/<stock_code>')
def stock_pe_chart(stock_code):
    this_year = int(time.strftime("%Y"))
    start_year = str(this_year - 6)
    start_date = start_year + '0101'

    pe_df = stock_service.find_pe_df(stock_code, start_date)

    pe_df.set_index(pe_df['trade_date'], inplace=True)
    pe_df = pe_df.transpose()
    pe_df = pe_df.sort_index(axis=1, ascending=False)
    pe_df = pe_df.loc['pe_ttm':'pe_ttm', :]

    jsonData = {'pe': {} }
    jsonData['pe']['dates'] = pe_df.columns.values.tolist()
    jsonData['pe']['data'] = []

    data = json.loads(pe_df.to_json(orient="values"))
    for d in data:
        tmp = {}
        tmp['name'] = 'pe'
        tmp['data'] = d
        tmp['type'] = 'line'
        jsonData['pe']['data'].append( tmp )

    return jsonify(jsonData)
