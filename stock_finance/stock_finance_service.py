import json

import pandas as pd
from pandas.tseries.offsets import QuarterEnd, DateOffset
import tushare as ts

from setting import ts_api


# 分析股票
from stock import stock_service


def finance_analyse(stock_code, start_date):
    income_df = ts_api.income(ts_code=stock_code, start_date=start_date)
    income_df.drop_duplicates(subset='end_date', keep='first', inplace=True)
    balancesheet_df = ts_api.balancesheet(ts_code=stock_code, start_date=start_date)
    balancesheet_df.drop_duplicates(subset='end_date', keep='first', inplace=True)
    cashflow_df = ts_api.cashflow(ts_code=stock_code, start_date=start_date)
    cashflow_df.drop_duplicates(subset='end_date', keep='first', inplace=True)
    fina_indicator_df = ts_api.fina_indicator(ts_code=stock_code, start_date=start_date)
    fina_indicator_df.drop_duplicates(subset='end_date', keep='first', inplace=True)

    # 补充单季度数据
    add_quarter_data(income_df, 'total_revenue')  # 营业总收入
    add_quarter_data(income_df, 'total_profit')  # 营业总利润
    add_quarter_data(income_df, 'n_income')  # 净利润

    print('quarter_total_revenue')
    compute_yoy(income_df, 'quarter_total_revenue')
    print('quarter_total_profit')
    compute_yoy(income_df, 'quarter_total_profit')
    print('quarter_n_income')
    compute_yoy(income_df, 'quarter_n_income')

    # 合并数据
    df = pd.merge(income_df, balancesheet_df, on='end_date')
    df = pd.merge(df, cashflow_df, on='end_date')
    df = pd.merge(df, fina_indicator_df, on='end_date')

    # 格式化数据
    df['end_date'] = df['end_date'].apply(lambda x: x[2:6])
    df.set_index(df['end_date'], inplace=True)

    df[['total_revenue', 'total_profit', 'n_income',
        'accounts_receiv', 'adv_receipts', 'inventories',
        'n_cashflow_act', 'n_cashflow_inv_act', 'n_cash_flows_fnc_act', 'free_cashflow']] \
        = df[['total_revenue', 'total_profit', 'n_income',
            'accounts_receiv', 'adv_receipts', 'inventories',
            'n_cashflow_act', 'n_cashflow_inv_act', 'n_cash_flows_fnc_act', 'free_cashflow']] / 100000000

    df = df[['total_revenue', 'total_profit', 'n_income',
             'yoy_quarter_total_revenue', 'yoy_quarter_total_profit', 'yoy_quarter_n_income',
             'roe', 'roe_dt', 'grossprofit_margin', 'debt_to_assets', 'accounts_receiv', 'adv_receipts',
             'inventories', 'n_cashflow_act', 'n_cashflow_inv_act', 'n_cash_flows_fnc_act', 'free_cashflow'
             ]]
    df = df.fillna(value=0)
    df = df.round(2)
    df = df.rename(columns={'n_income': '净利润',
                            'total_revenue': '营业总收入',
                            'total_profit': '营业总利润',
                            'yoy_quarter_total_revenue': '总收入季度增长率',
                            'yoy_quarter_total_profit': '总利润季度增长率',
                            'yoy_quarter_n_income': '净利润季度增长率',
                            'roe': '净资产收益率',
                            'roe_dt': '净资产收益率扣非',
                            'grossprofit_margin': '销售毛利率',
                            'debt_to_assets': '资产负债率',
                            'accounts_receiv': '应收账款',
                            'adv_receipts': '预收款项',
                            'inventories': '存货',
                            'n_cashflow_act': '经营现金流量净额',
                            'n_cashflow_inv_act': '投资现金流量净额',
                            'n_cash_flows_fnc_act': '筹资现金流量净额',
                            'free_cashflow': '企业自由现金流量',
                            'rd_exp': '研发费用',
                            'rd_exp_per': '研发收入比'
                            })

    return df


# 添加季度数据
def add_quarter_data(df, label):
    quarter_label = 'quarter_'+label
    df[quarter_label] = None
    for index, line in df.iterrows():
        # 计算每个季度的总收入
        if '0331' == line['end_date'][4:]:
            df.loc[index, quarter_label] = line[label]
        else:
            this_quarter = pd.Timestamp(line['end_date'])
            last_quarter = (this_quarter - QuarterEnd(n=1)).strftime("%Y%m%d")
            tmp = df[df.end_date == last_quarter]
            if not tmp.empty:
                last_quarter_line = tmp.iloc[-1]
                df.loc[index, quarter_label] = line[label] - last_quarter_line[label]

        # print(line['end_date'], income_df.loc[index, quarter_label])


# 计算同比增长
def compute_yoy(df, label):
    start_year = df.iloc[-1]['end_date'][:4]
    yoy_label = 'yoy_' + label
    df[yoy_label] = None
    for index, line in df.iterrows():
        # 计算每个季度的总收入
        if start_year != line['end_date'][:4]:
            this_year = pd.Timestamp(line['end_date'])
            last_year = (this_year - DateOffset(years=1)).strftime("%Y%m%d")
            tmp = df[df.end_date == last_year]
            if not tmp.empty:
                last_year_line = tmp.iloc[-1]
                if last_year_line[label] is not None and line[label] is not None:
                    print(label, line)
                    print(line[label], last_year_line[label])
                    df.loc[index, yoy_label] = (line[label] - last_year_line[label]) / last_year_line[label] * 100

                    # print(line['end_date'], "%0.2f%%" % df.loc[index, yoy_label] )


# 返回表格json
def fetch_finance_data(stock_code, finance_df):
    finance_df = finance_df.transpose()
    finance_df.insert(0, '类目', finance_df.index)

    jsonData = {}
    jsonData['data'] = json.loads(finance_df.to_json(orient="records"))
    jsonData['dates'] = finance_df.columns.values.tolist()

    df = ts_api.namechange(ts_code=stock_code, fields='ts_code,name,start_date,end_date,change_reason')
    jsonData['stock_name'] = df.loc[0, 'name']

    return jsonData


# 分析股票
def analyse_chart(finance_df, pe_df, stock_price_max_min_df, price_df ):

    jsonData = {'q_increase_percentage': {},
                'stock_price': {}}

    merged_df = pd.merge(stock_price_max_min_df, finance_df, left_index=True, right_index=True, how='left')

    merged_df = merged_df.transpose()
    merged_df = merged_df.sort_index(axis=1, ascending=False)
    # 财务
    merged_df.insert(0, '类目', merged_df.index)
    finance_df = merged_df['总收入季度增长率':'净利润季度增长率']
    jsonData['q_increase_percentage']['dates'] = finance_df.columns.values.tolist()[1:-1]
    jsonData['q_increase_percentage']['data'] = []
    data = json.loads(finance_df.to_json(orient="values"))

    for d in data:
        tmp = {}
        tmp['name'] = d[0]
        tmp['data'] = d[1:-1]
        tmp['type'] = 'line'
        tmp['yAxisIndex'] = 0
        tmp['xAxisIndex'] = 0
        jsonData['q_increase_percentage']['data'].append( tmp )

    # 股价
    stock_price_max_min_df = merged_df['max':'min']
    jsonData['stock_price']['dates'] = stock_price_max_min_df.columns.values.tolist()[1:-1]
    jsonData['stock_price']['data'] = []
    data = json.loads(stock_price_max_min_df.to_json(orient="values"))

    d = data[0]
    price_tmp = {}
    price_tmp['name'] = '股价max'
    price_tmp['data'] = d[1:-1]
    price_tmp['type'] = 'line'
    price_tmp['yAxisIndex'] = 1
    price_tmp['xAxisIndex'] = 0
    jsonData['stock_price']['data'].append(price_tmp)
    d = data[1]
    price_tmp = {}
    price_tmp['name'] = '股价min'
    price_tmp['data'] = d[1:-1]
    price_tmp['type'] = 'line'
    price_tmp['yAxisIndex'] = 1
    price_tmp['xAxisIndex'] = 0
    jsonData['stock_price']['data'].append(price_tmp)

    # 股价日线
    price_df = price_df.transpose()
    # price_df = price_df.sort_index(axis=1, ascending=False)
    price_df = price_df['close':]
    data = json.loads(price_df.to_json(orient="values"))
    d = data[0]
    price_tmp = {}
    price_tmp['name'] = '股价'
    price_tmp['data'] = d[1:-1]
    price_tmp['type'] = 'line'
    price_tmp['yAxisIndex'] = 1
    price_tmp['xAxisIndex'] = 1
    jsonData['stock_price']['data'].append(price_tmp)
    jsonData['stock_price']['dates2'] = price_df.columns.values.tolist()[1:-1]

    return jsonData


# 获取股价季度最高、最低
def fetch_stock_max_min_price(stock_code, start_date):
    df = stock_service.find_stock_daily_price_df(stock_code, start_date)

    df.reset_index(drop=True, inplace=True)

    df['trade_date'] = df['trade_date'].apply(lambda x: ajust_date_to_quarter(x))

    df = df[['trade_date', 'close']]
    df_max = df.groupby('trade_date').max().rename(columns={'close': 'max'})
    df_min = df.groupby('trade_date').min().rename(columns={'close': 'min'})
    df_max_min = pd.merge(df_max, df_min, on='trade_date')

    return [df, df_max_min]


# 调整为季度数据
def ajust_date_to_quarter(x):
    month = x[4:6]
    if month == '01' or month == '02' or month == '03':
        return x[2:4] + '03'
    elif month == '04' or month == '05' or month == '06':
        return x[2:4] + '06'
    elif month == '07' or month == '08' or month == '09':
        return x[2:4] + '09'
    else:
        return x[2:4] + '12'
