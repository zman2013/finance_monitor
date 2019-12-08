import datetime
import os

import pandas as pd

import setting


dir_path = setting.root_dir + '/pe/'
if os.path.exists(dir_path) == False:
    os.makedirs(dir_path)


# 加载股票日线信息
def load_pe(index_code, start_date=None):
    df = None
    try:
        df = pd.read_csv(dir_path+index_code+".pe")

        date_index = pd.to_datetime(df['searchDate'], format='%Y-%m-%d')
        df.set_index(date_index, inplace=True)

        # df['trade_date2'] = df['trade_date'].apply(lambda x: pd.to_datetime(x, format='%Y%m%d'))

    except Exception as e:
        print(e)
        print( 'load pe from file failed')

    if start_date is not None:
        start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
        for index in df.index:
            if index.date() < start_date:
                df = df.drop(index=index)

    if df is not None:
        df['trade_date'] = df['searchDate'].apply(str)
    return df


# 保存指数pe信息
def save_pe(index_code, df):
    # 加载已有数据
    pe_df = load_pe(index_code=index_code)
    # 新旧数据拼接
    if pe_df is not None and df is not None:
        pe_df = df.append(pe_df, ignore_index=True)
    # 去重
    if pe_df is not None:
        pe_df = pe_df.drop_duplicates(subset='searchDate')
    else:
        pe_df = df
    # 排序
    date_index = pd.to_datetime(pe_df['searchDate'], format='%Y-%m-%d')
    pe_df.set_index(date_index, inplace=True)
    pe_df = pe_df.sort_index(ascending=False)

    # 写入文件
    file_path = dir_path + index_code + ".pe"
    pe_df.to_csv(file_path, index=False)
