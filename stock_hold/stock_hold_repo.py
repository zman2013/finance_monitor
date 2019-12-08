import os

import pandas as pd

import setting

dir_path = setting.root_dir + '/stock_hold'
if os.path.exists(dir_path) == False:
    os.makedirs(dir_path)
file_path = dir_path + '/list.csv'


# 加载持有的股票列表
def load():
    df = None
    try:
        df = pd.read_csv(file_path)
    except:
        print('load hold stock list from file failed')
    return df


# 输出持有的股票
def save(df):
    df.to_csv(file_path, index_label=False)
