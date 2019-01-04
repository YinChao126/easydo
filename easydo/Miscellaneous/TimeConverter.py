# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 10:59:27 2018

@author: yinchao
"""

from datetime import datetime
from datetime import timedelta

    
def str2dtime(str_time):
    '''
    str类型的时间转换为datetime类型的时间
    支持 . / - 等时间格式
    '''
    separator = str_time[4]
    if separator >= '0' and separator <= '9':
        day_formate = '%Y%m%d'
    elif separator == '-':
        day_formate = '%Y-%m-%d'
    elif separator == '/':
        day_formate = '%Y/%m/%d'
    elif separator == '.':
        day_formate = '%Y.%m.%d'
    return datetime.strptime(str_time,day_formate)
 

def dtime2str(dtime,separator = ''):
    '''
    格式转换
    datetime格式转为str
    '''
    day_formate = '%Y' + separator + '%m' + separator + '%d'
    return dtime.strftime(day_formate)

if __name__ == '__main__':
    a = str2dtime('20181201') 
    b =dtime2str(a,'/')
    print(b)