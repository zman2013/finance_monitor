import datetime
import os
import time
import traceback

import pandas as pd
from pandas.tseries.offsets import QuarterEnd

from setting import ts_api, root_dir
from stock_finance import stock_finance_service

# 筛选的股票目录
dir_path = root_dir + '/stock_choose'
if os.path.exists(dir_path) == False:
    os.makedirs(dir_path)
# 筛选的股票目录下的财务数据目录
finance_dir_path = dir_path + '/finance/'
if os.path.exists(finance_dir_path) == False:
    os.makedirs(finance_dir_path)
# 筛选出的优质股票文件路径
good_stock_file_path = dir_path + '/good_stocks'
# 已经分析过的股票
analysed_stock_file_path = dir_path + '/analysed_stocks'


# 加载分析完成的股票
def load_good_stock_by_quarter():
    df = pd.read_csv(good_stock_file_path)
    latest_quarter_label = df.columns[3]  # 最近一个季度
    df['latest_quarter_float'] = df[latest_quarter_label].apply(lambda value: floatString(value))
    df = df.sort_values(by='latest_quarter_float', ascending=False)
    return df


def floatString(value):
    if value == 'nan%':
        return 0
    else:
        return float(value[:-2])


# 最近四个季度营收、利润增速>10%
def select_by_quarter():
    df = ts_api.stock_basic(exchange='', list_status='L', fields='ts_code,name,industry')

    # 获取近两年的数据
    this_year = int(time.strftime("%Y"))
    start_year = str(this_year - 2)
    start_date = start_year + '0101'

    # 加载已分析过的股票信息, 第一列作为index
    if os.path.exists(analysed_stock_file_path):
        analysed_stocks = pd.read_csv(analysed_stock_file_path, index_col=0)
        if os.path.exists(good_stock_file_path):
            good_stocks = pd.read_csv(good_stock_file_path, index_col=0)
        else:
            good_stocks = []
    else:
        analysed_stocks = pd.DataFrame({})
        good_stocks = []

    # 遍历每一个股票（即：每一行）
    for index, line in df.iterrows():
        ts_code = line['ts_code']

        # 检查是否已经处理过了，如果处理过了，直接跳过
        if ts_code in analysed_stocks.index:
            print( ts_code, ' already analysed, skip')
            continue
        # 默认置为处理成功
        analysed_stocks.at[ts_code, 'result'] = 'success'

        stock_finance_dir_path = finance_dir_path + ts_code
        if not os.path.exists(stock_finance_dir_path):
            os.makedirs(stock_finance_dir_path)

        try:
            if os.path.exists(stock_finance_dir_path + "/income_df"):
                income_df = pd.read_csv(stock_finance_dir_path + "/income_df")
                today = datetime.datetime.today().date()
                last_quarter = (today - QuarterEnd(n=1))
                end_date = last_quarter.strftime("%Y%m%d")

                income_end_date = income_df.iloc[0]["end_date"]
                if str(income_end_date) == end_date:
                    cashflow_df = pd.read_csv(stock_finance_dir_path + "/cashflow_df")
                else:
                    print("downloading " + ts_code)
                    time.sleep(1)
                    income_df = analyse_income_df(ts_code, start_date)
                    cashflow_df = analyse_cashflow(ts_code, start_date)

                    income_df.to_csv(stock_finance_dir_path + "/income_df", index=False)
                    cashflow_df.to_csv(stock_finance_dir_path + "/cashflow_df", index=False)
            else:
                print("downloading " + ts_code)
                time.sleep(1)
                income_df = analyse_income_df(ts_code, start_date)
                cashflow_df = analyse_cashflow(ts_code, start_date)

                income_df.to_csv(stock_finance_dir_path + "/income_df", index=False)
                cashflow_df.to_csv(stock_finance_dir_path + "/cashflow_df", index=False)

            # 判断前四条数据（即最近四个季度）：季度营收同比、季度利润增速都>10
            for income_df_index, income_df_line in income_df.iterrows():
                # 净利润小于1亿，忽略
                if income_df_line['n_income'] < 100000000:
                    print("income < 100m stock[%s]" % ts_code)
                    break
                if income_df_line['yoy_quarter_total_revenue'] < 10 \
                        or income_df_line['yoy_quarter_total_profit'] < 10 \
                        or income_df_line['yoy_quarter_n_income'] < 10:
                        #or cashflow_df.loc[income_df_index, 'n_cashflow_act'] < 0:  # 经营现金流现金流为正
                    print("bad stock[%s]" % ts_code, income_df_line)
                    break
                if income_df_index == 3:
                    print("good stock[%s]" % ts_code)
                    with open('/tmp/select_by_quarter_good_stock_code.txt', mode='a+') as file:
                        file.write("%s\n" % ts_code)

                    stock_info = {}
                    stock_info['ts_code'] = ts_code
                    stock_info['name'] = line['name']
                    stock_info['industry'] = line['industry']
                    first_index = income_df.index[0]
                    second_index = income_df.index[1]
                    third_index = income_df.index[2]
                    date = income_df.loc[first_index, 'end_date']
                    date = str(date)
                    stock_info[date] = "%0.1f%%" % income_df.loc[first_index, 'yoy_quarter_total_revenue']
                    date = income_df.loc[second_index, 'end_date']
                    date = str(date)
                    stock_info[date] = "%0.1f%%" % income_df.loc[second_index, 'yoy_quarter_total_revenue']
                    date = income_df.loc[third_index, 'end_date']
                    date = str(date)
                    stock_info[date] = "%0.1f%%" % income_df.loc[third_index, 'yoy_quarter_total_revenue']

                    # 获取pe
                    this_year = int(time.strftime("%Y"))
                    pe_start_date = str(this_year) + '0101'
                    pe_df = ts_api.daily_basic(ts_code=ts_code, start_date=pe_start_date)
                    cashflow_df.to_csv(stock_finance_dir_path + "/pe_df", index=False)
                    stock_info['pe'] = "%0.1f" % pe_df.loc[0, 'pe']

                    good_stocks.append(stock_info)

                    # 每次都记录，防止被服务器禁掉了
                    df = pd.DataFrame(good_stocks)
                    df.to_csv(good_stock_file_path, index=False)

                    break
        except Exception as e:
            print("analyse stock[%s] failed" % ts_code)
            traceback.print_exc()
            analysed_stocks.at[ts_code, 'result'] = 'fail'
        # 没处理完一支股票，都存储到文件中
        analysed_stocks.to_csv(analysed_stock_file_path)

    df = pd.DataFrame(good_stocks)

    df.to_csv(good_stock_file_path, index=False)

    return good_stocks


# 分析股票
def analyse_income_df(stock_code, start_date):
    income_df = ts_api.income(ts_code=stock_code, start_date=start_date)
    income_df.drop_duplicates(subset='end_date', keep='first', inplace=True)

    # 补充单季度数据
    stock_finance_service.add_quarter_data(income_df, 'total_revenue')  # 营业总收入
    stock_finance_service.add_quarter_data(income_df, 'total_profit')  # 营业总利润
    stock_finance_service.add_quarter_data(income_df, 'n_income')  # 净利润

    stock_finance_service.compute_yoy(income_df, 'quarter_total_revenue')
    stock_finance_service.compute_yoy(income_df, 'quarter_total_profit')
    stock_finance_service.compute_yoy(income_df, 'quarter_n_income')

    # 由于去掉了重复项，导致index已经不连续了，设置index为end_date
    date_index = pd.to_datetime(income_df['end_date'], format='%Y%m%d')
    income_df.set_index(date_index, inplace=True)

    return income_df


# 分析现金流
def analyse_cashflow(stock_code, start_date):
    cashflow_df = ts_api.cashflow(ts_code=stock_code, start_date=start_date)
    cashflow_df.drop_duplicates(subset='end_date', keep='first', inplace=True)

    # 由于去掉了重复项，导致index已经不连续了，设置index为end_date
    date_index = pd.to_datetime(cashflow_df['end_date'], format='%Y%m%d')
    cashflow_df.set_index(date_index, inplace=True)

    return cashflow_df

# select_by_quarter()



