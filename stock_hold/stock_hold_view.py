from flask import Blueprint
from flask import jsonify
from flask import render_template
from stock_hold import stock_hold_service

bp = Blueprint('stock_hold', __name__, url_prefix='/stock_hold')


@bp.route('/view')
def view():
    return render_template("stock_hold/view.html")


@bp.route('/json')
def info():
    hold_stock_info_json = stock_hold_service.fetch_hold_stock_info()
    json_data = {
        'data': hold_stock_info_json
    }
    return jsonify(json_data)


@bp.route('/download')
def download():
    result = stock_hold_service.download_hold_stock_info()
    json_data = {
        'data': result
    }
    return jsonify(json_data)
