import json

from flask import Blueprint, jsonify
from flask import render_template

from stock_choose import stock_choose_service

bp = Blueprint('stock_choose', __name__, url_prefix='/stock_choose')


@bp.route('/view')
def view():
    return render_template("stock_choose/view.html")


@bp.route('/json')
def load_json():
    df = stock_choose_service.load_good_stock_by_quarter()

    json_data = {'data': json.loads(df.to_json(orient="records")),
                'dates': df.columns.values.tolist()[3:6]}

    return jsonify(json_data)


@bp.route('/download')
def download_choose_good_stock():
    stock_choose_service.select_by_quarter()

    json_data = {"success": True}
    return jsonify(json_data)
