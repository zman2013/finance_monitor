import time

from flask import Blueprint, request
from flask import render_template
from flask import jsonify

from country_database import country_database_service

bp = Blueprint('country_database', __name__, url_prefix='/country_database')


# 自定义指标的页面
@bp.route('/customized_view')
def customized_view():
    return render_template("country_database/customized_view.html")


# 基本指标的页面
@bp.route('/basic_view')
def basic_view():
    return render_template("country_database/basic_view.html")


# 获取菜单列表
@bp.route('/item_options')
def item_options(dbcode='hgyd', wdcode='zb', m='getTree'):
    # 处理参数
    id = request.args['id']
    # 请求指标菜单
    items = country_database_service.fetch_items_df(id, dbcode, wdcode, m)

    return jsonify(items)


@bp.route('/query_data')
def info(dbcode='hgyd', rowcode='zb', colcode='sj', wds=[], h=1, m='QueryData'):
    # 处理参数
    dfwds = [{'wdcode': request.args['wdcode'],
              'valuecode': request.args['valuecode']},
             {'wdcode': 'sj',
              'valuecode': request.args['sj_valuecode']
             }]
    k1 = int(time.time()) * 1000

    # 获取数据
    df = country_database_service.query_data_df(dbcode, rowcode, colcode, wds, dfwds, k1, h, m)

    # 转置
    df = df.transpose()
    # 将0置为空
    df[df == 0] = ''

    # 构建response
    response = {'index': df.columns.values.tolist(),
                'names': df.index.values.tolist(),
                'data': []}

    for index, row in df.iterrows():
        tmp = {'name': row.name,
               'data': row.values.tolist(),
               'type': 'line',
               'smooth': True,
               'symbol': 'none',
               'sampling': 'average'
               }
        response['data'].append(tmp)

    json = jsonify(response)
    return json
