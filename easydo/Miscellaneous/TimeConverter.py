# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 10:59:27 2018

@author: yinchao

时间处理模块
APP一览表：
str2dtime:输入一个str类型的时间，转换为datetime格式
dtime2str:输入datetime时间，转换为str格式（默认'xxxx-xx-xx'）
is_equal:判断两个日期是否相等
"""

from datetime import datetime
from datetime import timedelta

    
def str2dtime(str_time):
    '''
    str类型的时间转换为datetime类型的时间
    @输入：str类型的时间
    @输出：datetime类型的时间（只有日期，时间统一为0）
    @备注：支持 ". / - "等各种时间格式
          月份和日期必须保证 xx, xx 比如：01 03
    '''
    separator = str_time[4]
    if separator <= '9' and separator >= '0':
        separator = ''
    day_formate = '%Y' + separator + '%m' + separator + '%d'
    return datetime.strptime(str_time,day_formate)
 

def dtime2str(dtime,separator = ''):
    '''
    格式转换
    datetime格式转为str
    '''
    day_formate = '%Y' + separator + '%m' + separator + '%d'
    return dtime.strftime(day_formate)

def is_equal(time1, time2):
    '''
    @描述：判断两个日期是否相等
    @输入：time1/time2->两个时间，可以是str格式，亦可以是datetime格式
    @输出：True->相等， False->不等
    '''
    if isinstance(time1, str):
        time1 = str2dtime(time1)
    if isinstance(time2, str):
        time2 = str2dtime(time2)
    return dtime2str(time1) == dtime2str(time2)
    
    
if __name__ == '__main__':
    a = str2dtime('2018/2/1') 
    print(a)
#    b =dtime2str(a,'/')
#    print(b)