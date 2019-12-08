import time

from flask import Blueprint, jsonify
from flask import render_template

from stock_finance import stock_finance_service
from stock import stock_service


bp = Blueprint('stock_finance', __name__, url_prefix='/stock_finance')


@bp.route('/view/<stock_code>')
def stock_finance(stock_code):

    context = {
        'stock_code': stock_code
    }

    return render_template("stock_finance/view.html", **context)


@bp.route('/table/json/<stock_code>')
def stock_analysis(stock_code):
    this_year = int(time.strftime("%Y"))
    start_year = str(this_year - 6)
    start_date = start_year + '0101'

    df = stock_finance_service.finance_analyse(stock_code, start_date)
    json = stock_finance_service.fetch_finance_data(stock_code, df)

    return jsonify(json)


@bp.route('/chart/json/<stock_code>')
def stock_analysis_chart(stock_code):
    this_year = int(time.strftime("%Y"))
    start_year = str(this_year - 6)
    start_date = start_year + '0101'

    df = stock_finance_service.finance_analyse(stock_code, start_date)

    # 先强制下载，再load，保证数据最新（load是从文件中load，不会自动刷新）
    stock_service.download_pe_df(stock_code, start_date)
    pe_df = stock_service.find_pe_df(stock_code, start_date)
    stock_service.download_daily_df(stock_code, start_date)
    [stock_price_max_min_df, stock_price_df] = stock_finance_service.fetch_stock_max_min_price(stock_code, start_date)

    json = stock_finance_service.analyse_chart(df, pe_df, stock_price_df, stock_price_max_min_df)
    return jsonify(json)

