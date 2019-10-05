# 国家统计局数据
import time

import requests

import pandas as pd


# 从国家统计局获取指标数据
def fetch_items_df(id, dbcode, wdcode, m):
    url = "http://data.stats.gov.cn/easyquery.htm"

    header = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'data.stats.gov.cn',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0(Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    }

    para = {
        'id': id,
        'dbcode': dbcode,
        'wdcode': wdcode,
        'm': m
    }

    print(url)
    print(header)
    print(para)
    r = requests.post(url, params=para, headers=header)
    print(r.status_code)
    print(r.headers)
    print(r.content)

    items = []

    json = r.json()

    for index, item in enumerate(json):
        print(item['dbcode'], item['id'], item['isParent'], item['wdcode'], item['name'])
        items.append(item)

    return items


# 查询数据
def query_data_df(dbcode, rowcode, colcode, wds, dfwds, k1, h, m):
    url = "http://data.stats.gov.cn/easyquery.htm"

    header = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'data.stats.gov.cn',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0(Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    }

    # 转化为字符串，使用方法str不行
    dfwdsStr = '['
    for items in dfwds:
        dfwdsStr = dfwdsStr + '{'
        for key in items:
            dfwdsStr = dfwdsStr+'"'+key+'":"'+str(items[key])+'",'
        dfwdsStr = dfwdsStr + '},'
    dfwdsStr = dfwdsStr+']'
    # 准备参数
    para = {'m': m,
            'dbcode': dbcode,
            'rowcode': rowcode,
            'colcode': colcode,
            'wds': str(wds),
            'dfwds': dfwdsStr,
            'k1': k1,
            'h': h}

    # 发起请求
    print(url)
    print(header)
    print(para)
    r = requests.post(url, params=para, headers=header)
    print(r.status_code)
    print(r.headers)
    print(r.content)

    # 转化结果数据
    response_json = r.json()['returndata']
    # 提取指标code和名称
    # zb是指标的简写，sj是时间的简写
    zb_name_map = {}
    for node in response_json['wdnodes'][0]['nodes']:
        name = node['name']
        zbcode = node['code']
        zb_name_map[zbcode] = name

    # 提取指标数据
    data_dict = {}
    for node in response_json['datanodes']:
        zbcode = node['wds'][0]['valuecode']
        zbname = zb_name_map[zbcode]            # 指标名称
        sjcode = node['wds'][1]['valuecode']    # 时间
        value = node['data']['data']            # 值

        if data_dict.__contains__(zbname):
            zb_dict = data_dict[zbname]
            zb_dict[sjcode] = value
        else:
            data_dict[zbname] = {
                sjcode: value
            }

    # 转化dict为df
    df = pd.DataFrame(data_dict)

    return df

# 获取指标列表
# df = fetch_items_df('zb', 'hgyd', 'zb', 'getTree')

# 查询数据
# dfwds = [{"wdcode":"zb","valuecode":"A0202"},]
# k1 = int(time.time()) * 1000
# df = query_data_df(dbcode='hgyd', rowcode='zb', colcode='sj', wds=[], dfwds=dfwds, k1=k1, h=1, m='QueryData')

# pat = re.compile(r'(\\x[0-9a-fA-F][0-9a-fA-F])+')
# line = "\\xe4\\xbb\\xb7\\xe6\\xa0\\xbc\\xe6\\x8c\\x87\\xe6\\x95\\xb0"
# for m in re.finditer(pat,line):
#             print(m.group())
# print(re.sub(pat, ti, line))