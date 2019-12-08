import time

import pandas as pd
from flask import Blueprint, request
from flask import render_template
from flask import jsonify

from stock_index import index_service
from country_database import country_database_service

bp = Blueprint('country_database_m2', __name__, url_prefix='/country_database_m2')


# 自定义指标的页面
@bp.route('/view')
def customized_view():
    return render_template("country_database_m2/view.html")


@bp.route('/json')
def info(dbcode='hgyd', rowcode='zb', colcode='sj', wds=[], h=1, m='QueryData'):
    # 处理参数
    dfwds = [{'wdcode': "zb",
              'valuecode': "A0D01"},
             {'wdcode': 'sj',
              'valuecode': "LAST160"}]

    k1 = int(time.time()) * 1000

    # 获取m2数据
    m2_df = country_database_service.query_data_df(dbcode, rowcode, colcode, wds, dfwds, k1, h, m)

    # 获取指数数据
    index_df = index_service.load_sh_index_df(start_date='20060101')
    index_df['trade_date_column'] = index_df['trade_date'].apply(lambda x: str(x)[:6])
    index_df = index_df.groupby('trade_date_column').max().rename(columns={'close': 'max'})
    index_df = index_df.rename(columns={'max': '上证'})

    # 加工数据
    df = pd.merge(m2_df, index_df, left_index=True, right_index=True)
    df['M0同比'] = df['流通中现金(M0)供应量_同比增长']
    df['M1同比'] = df['货币(M1)供应量_同比增长']
    df['M2同比'] = df['货币和准货币(M2)供应量_同比增长']
    df['M1同比-M2同比'] = df['货币(M1)供应量_同比增长'] - df['货币和准货币(M2)供应量_同比增长']

    # 转置
    df = df.transpose()
    # 将0置为空
    df[df == 0] = ''

    # 提取目标指标
    m2_df = df.loc[['M0同比', 'M1同比', 'M2同比', 'M1同比-M2同比'], :]
    index_df = df.loc[['上证'], :]

    # 构建response
    names = index_df.index.values.tolist() + m2_df.index.values.tolist()
    response = {'index': m2_df.columns.values.tolist(),
                'names': names,
                'm2': [],
                'sh_index': []}

    # 构建m2数据
    for index, row in m2_df.iterrows():
        tmp = {'name': row.name,
               'data': row.values.tolist(),
               'type': 'line',
               'smooth': True,
               'symbol': 'none',
               'sampling': 'average'
               }
        response['m2'].append(tmp)

    # 构建上证指数数据
    for index, row in index_df.iterrows():
        tmp = {'name': row.name,
               'data': row.values.tolist(),
               'type': 'line',
               'smooth': True,
               'symbol': 'none',
               'sampling': 'average',
               'yAxisIndex': 1
               }
        response['sh_index'].append(tmp)

    json = jsonify(response)
    return json
