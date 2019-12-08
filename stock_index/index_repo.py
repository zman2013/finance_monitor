import datetime
import os

import pandas as pd

import setting


dir_path = setting.root_dir + '/index/'
if os.path.exists(dir_path) == False:
    os.makedirs(dir_path)


# 加载股票日线信息
def load_daily(index_code, start_date):
    df = None
    try:
        df = pd.read_csv(dir_path+index_code)
        date_index = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        df.set_index(date_index, inplace=True)

    except:
        print( 'load stock daily price from file failed')

    if start_date is not None:
        start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
        for index in df.index:
            if index.date() < start_date:
                df = df.drop(index=index)

    if df is not None:
        df['trade_date'] = df['trade_date'].apply(str)
    return df


# 保存股票日线信息
def save_daily(index_code, df):
    old_df = load_daily(index_code=index_code, start_date=None)
    if old_df is not None:
        df = df.append(old_df, ignore_index=True)

        # 排序
        date_index = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        df.set_index(date_index, inplace=True)
        df = df.sort_index(ascending=False)

        # 去重
        df = df.drop_duplicates(subset='trade_date', keep='first')

    file_path = dir_path + index_code
    df.to_csv(file_path, index=False)
