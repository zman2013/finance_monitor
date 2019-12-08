import datetime

import tushare as ts

from stock_index import index_repo
from setting import ts_api


# 获取sh stock_index df
def load_sh_index_df(start_date):
    df = index_repo.load_daily('000001.SH', start_date)
    return df


# 获取sz stock_index df
def load_sz_index_df(start_date):
    df = index_repo.load_daily('399001.SZ', start_date)
    return df


# 下载sh index并保存到本地
def download_sh_index(start_date=None):
    index_code = '000001.SH'
    df = download(index_code, start_date, asset='I')
    # df['trade_date'] = df['trade_date'].apply(lambda x: pd.to_datetime(x, format='%Y%m%d'))
    index_repo.save_daily(index_code, df)


# 下载sz index并保存到本地
def download_sz_index(start_date=None):
    index_code = '399001.SZ'
    df = download(index_code, start_date, asset='I')
    # df['trade_date'] = df['trade_date'].apply(lambda x: pd.to_datetime(x, format='%Y%m%d'))
    index_repo.save_daily(index_code, df)


# load_available_dates
def load_available_dates():
    index_df = load_sh_index_df(start_date=None)
    dates = []
    for date in index_df['trade_date']:
        date = datetime.datetime.strptime(str(date), '%Y%m%d').date()
        dates.append(date)
    return dates


# 下载tu_share日线数据
def download(code, start_date=None, asset='E', adj=None):

    delta_year = 5

    df = None

    today = datetime.datetime.today().date()

    if start_date is None:
        start_date = datetime.date(today.year - delta_year, today.month, today.day)
        start_date_formatted = start_date.strftime('%Y%m%d')
        df = ts.pro_bar(api=ts_api, ts_code=code, asset=asset, adj=adj, start_date=start_date_formatted)
    else:
        start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
        while today > start_date:
            start_date_formatted = start_date.strftime('%Y%m%d')
            end_date = datetime.date(start_date.year + delta_year, start_date.month, start_date.day)
            end_date_formatted = end_date.strftime('%Y%m%d')

            df2 = ts.pro_bar(api=ts_api, ts_code=code, asset=asset, adj=adj, start_date=start_date_formatted,
                             end_date=end_date_formatted)
            if df is not None:
                df = df2.append(df, ignore_index=True)
            else:
                df = df2

            start_date = end_date

    return df


# 分析指数
def analyse_index(start_date):

    # 加载指数数据
    sh_index_df = load_sh_index_df(start_date)
    sz_index_df = load_sz_index_df(start_date)

    # 分析指数
    [buy_date, buy_index, sell_date, sell_index] = analyse(sh_index_df, sz_index_df)

    sh_index_df = sh_index_df[['close', 'trade_date']]
    sz_index_df = sz_index_df[['close', 'trade_date']]
    return [buy_date, buy_index, sell_date, sell_index, sh_index_df, sz_index_df]


# 分析股票，并进行交易
def analyse(sh_index_df, sz_index_df):
    stock = Stock()

    # 买入日期、价格
    buy_date = []
    buy_index = []
    # 卖出日期、价格
    sell_date = []
    sell_index = []

    # 从最早时间点向后遍历股票，遇到关键点位就进行操作
    for index in range(len(sh_index_df)-80, -1, -1):
        data = sh_index_df.iloc[index]

        sh_index_check_result = check_point( index, sh_index_df)
        sz_index_check_result = check_point( index, sz_index_df)

        if sh_index_check_result != 'hold':
            stock.sh_index_point = sh_index_check_result
        if sz_index_check_result != 'hold':
            stock.sz_index_point = sz_index_check_result

        if stock.sh_index_point == 'buy' and stock.sz_index_point == 'buy':
            # if vol != 0:
            buy_date.append(data['trade_date'])
            buy_index.append(data['close'])
            # 既然买入了就重置状态
            stock.sh_index_point = 'hold'
            stock.sz_index_point = 'hold'
        elif stock.sh_index_point == 'sell' and stock.sz_index_point == 'sell':
            # if vol != 0:
            sell_date.append(data['trade_date'])
            sell_index.append(data['close'])
            # 既然卖出了就重置状态
            stock.sh_index_point = 'hold'
            stock.sz_index_point = 'hold'

    return [buy_date, buy_index, sell_date, sell_index]


# 判断是否为关键点位：'buy' 'sell' 'hold'
def check_point(index, index_df):
    data = index_df[index: index + 18]

    max_line = data.loc[data['close'].idxmax()]
    min_line = data.loc[data['close'].idxmin()]

    # 判断买入
    if max_line['trade_date'] > min_line['trade_date']:  # 最高点在最低点之后
        if max_line['trade_date'] == data.iloc[0]['trade_date']:  # 最高点就是今天
            # print( "max date %s price %0.2f, min date %s price %0.2f" % (max_line['trade_date'], max_line['close'], min_line['trade_date'], min_line['close']))
            return 'buy'    # 买入

    # 判断卖出 单日跌幅 > 3% from 上证日线，如果下跌趋势已成时（从最高最多下跌>5%），某日跌幅超过3%，接下来很可能继续跌
    data = index_df[index: index + 10]
    max_line = data.loc[data['close'].idxmax()]
    min_line = data.loc[data['close'].idxmin()]
    delta = (max_line['close'] - min_line['close']) / max_line['close']

    if delta > 0.05 and data.iloc[0]['pct_chg'] <= -3:
        return 'sell'

    # 判断卖出
    data = index_df[index : index+20]

    max_line = data.loc[data['close'].idxmax()]
    min_line = data.loc[data['close'].idxmin()]

    delta = (max_line['close'] - min_line['close']) / max_line['close']
    if max_line['trade_date'] < min_line['trade_date']:     # 最高点在最低点之前
        if delta > 0.091:                                    # 跌幅 > 9.1%
            if min_line['trade_date'] == data.iloc[0]['trade_date']:  # 最低点就是今天
                return 'sell'

    # 判断卖出
    data = index_df[index: index + 120]

    max_line = data.loc[data['close'].idxmax()]
    min_line = data.loc[data['close'].idxmin()]

    delta = (max_line['close'] - min_line['close']) / max_line['close']
    if max_line['trade_date'] < min_line['trade_date']:  # 最高点在最低点之前
        if delta > 0.15:  # 跌幅 > 6%
            if min_line['trade_date'] == data.iloc[0]['trade_date']:  # 最低点就是今天
                return 'sell'

    # 不操作
    return 'hold'


class Stock:
    sh_index_point = None
    sz_index_point = None
    stock_point = None
    vol = 0

# print( download_pe_df(stock_code='600690.SH', start_date='20190101'))