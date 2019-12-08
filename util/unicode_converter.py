"""
通过正则表达式转换unicode为中文
输入：2018\xe5\xb9\xb49\xe6\x9c\x88
输出：2018年9月
"""

import re

pat = re.compile(r'(\\x[0-9a-fA-F][0-9a-fA-F])+')


def unicodetostr( s ):
    strTobytes = []
    for i in s.split('\\x'):
        if i != '':
            num = int(i, 16)
            strTobytes.append(num)
    a = bytes(strTobytes).decode()
    return a


def ti(m):
    s = str(m.group())
    a = unicodetostr(s)
    return a


name = "\\xe7\\xb3\\xbb\\xe7\\xbb\\x9f\\xe7\\xb9\\x81\\xe5\\xbf\\x99, \\xe8\\xaf\\xb7\\xe7\\xa8\\x8d\\xe5\\x90\\x8e\\xe5\\x86\\x8d\\xe8\\xaf\\x95"
print(name)
name1 = re.sub(pat, ti, name)
print(name1)


