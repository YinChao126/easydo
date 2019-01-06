# -*- coding: utf-8 -*-
"""
Created on Sat Dec 22 01:04:20 2018

@author: YinChao
"""
import sys,os
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OTHER_DIR = BASE_DIR + r'\Algorithm'
sys.path.append(OTHER_DIR)
OTHER_DIR = BASE_DIR + r'\Miscellaneous'
sys.path.append(OTHER_DIR)
OTHER_DIR = BASE_DIR + r'\Data'
sys.path.append(OTHER_DIR)

import pandas as pd
from datetime import datetime
from datetime import timedelta
from Miscellaneous import TimeConverter
from Data import TushareApp

def create_test_invest_list():
    '''
    测试用例，用于生成测试用的invest_list，供投资收益计算模型使用
    返回一个示例的invset_list
    '''
    
    header = ['deal_time','id','amount','price','direction']
    invest_list =pd.DataFrame(columns=header)
    
    s = ['20121023','601012.SH','200','6.90','1']
    s = pd.Series(s,index=['deal_time','id','amount','price','direction'])
    invest_list = invest_list.append(s, ignore_index=True)
    
    s = ['20130114','000651.SZ','100','26.5','1']
    s = pd.Series(s,index=['deal_time','id','amount','price','direction'])
    invest_list = invest_list.append(s, ignore_index=True)
    
    s = ['20140506','000651.SZ','200','30.00','1']
    s = pd.Series(s,index=['deal_time','id','amount','price','direction'])
    invest_list = invest_list.append(s, ignore_index=True)
    
    s = ['20161122','601012.SH','200','13.9','1']
    s = pd.Series(s,index=['deal_time','id','amount','price','direction'])
    invest_list = invest_list.append(s, ignore_index=True)
    return invest_list
    
class InvestRecordGenerator:
    '''
    @描述： 该类专门用来实现各种策略，生成可供回测的invest_list
    @已提供的策略：
    single_mode 每月固定时间点定投单支股票
    double_mode 每月固定时间定投两支股票，对半分
    '''
    def __init__(self,exchange_list, money, start_day, stop_day):
        '''
        初始化，
        exchange_list->投资组合，可以是单个股票，默认格式为str的id形式
        比如：['600660','510300']
        money:每月的定投额度
        start_day,stop_day:起止时间
        '''
        self.id_list = exchange_list
        self.money = money
        self.ts_app = TushareApp.ts_app()
        
        header = ['deal_time','id','amount','price','direction']
        self.invest_list =pd.DataFrame(columns=header)
        today = datetime.now()
        start = TimeConverter.str2dtime(start_day)
        stop = TimeConverter.str2dtime(stop_day)
        if stop > today:
            stop = today
#        print(today, start, stop)
        self.cur = start  
        self.stop = stop  
    def _get_last_month_day(self):
        month_list = []
        last_month = self.cur.month
        while self.cur < self.stop:
            cur_month = self.cur.month
            if last_month != cur_month:
                month_last_day = self.cur - timedelta(1) #last day of a month
#                print(month_last_day) #last month day
                month_list.append(month_last_day)
                last_month = cur_month
            self.cur += timedelta(1)
        return month_list
        
    def single_mode(self):
        id_str = self.id_list[0]
        for day in self._get_last_month_day():
            day_str = TimeConverter.dtime2str(day)
            price, day = self.ts_app.GetPrice(id_str,day_str)
            print(price,day)
            if price < 0.1:
                continue
            num_of_stock = int(self.money/price)
            item = {'deal_time':day, 
                    'id':id_str,
                    'amount':str(num_of_stock),
                    'price':str(price),
                    'direction':1}
            self.invest_list = self.invest_list.append(item,ignore_index=True)
        return self.invest_list
    
    def double_mode(self):
        for day in self._get_last_month_day():
            day_str = TimeConverter.dtime2str(day)
            price0, day0 = self.ts_app.GetPrice(self.id_list[0],day_str)
            price1, day1 = self.ts_app.GetPrice(self.id_list[1],day_str)
            if price0 < 0.1 and price1 < 0.1:
                continue
            elif price0 < 0.1:
                num_of_stock1 = int(self.money/2/price1)
                item1 = {'deal_time':day1, 
                        'id':self.id_list[1],
                        'amount':str(num_of_stock1),
                        'price':str(price1),
                        'direction':1}
                self.invest_list = self.invest_list.append(item1,ignore_index=True)
                print(day, price0, price1)
            elif price1 < 0.1:
                num_of_stock0 = int(self.money/2/price0)
                item0 = {'deal_time':day1, 
                        'id':self.id_list[1],
                        'amount':str(num_of_stock0),
                        'price':str(price1),
                        'direction':1}
                self.invest_list = self.invest_list.append(item0,ignore_index=True)
               
            else:
                num_of_stock0 = int(self.money/2/price0)
                num_of_stock1 = int(self.money/2/price1)
                item0 = {'deal_time':day0, 
                        'id':self.id_list[0],
                        'amount':str(num_of_stock0),
                        'price':str(price0),
                        'direction':1}
                self.invest_list = self.invest_list.append(item0,ignore_index=True)
                item1 = {'deal_time':day1, 
                        'id':self.id_list[1],
                        'amount':str(num_of_stock1),
                        'price':str(price1),
                        'direction':1}
                self.invest_list = self.invest_list.append(item1,ignore_index=True)
                print(day, price0, price1)
        return self.invest_list

if __name__ == '__main__':        
#a = method1('000651',10000,'20180101','20181221')
    #模式1，只投A
#    b = InvestRecordGenerator(['600660'],10000,'20180101','20181221')
#    record = b.single_mode()
#    print(b.single_mode()) 

    #模式2，A和B各投一半
    b = InvestRecordGenerator(['000651','600522'],10000,'20180101','20181221')
    print(b.double_mode())