# -*- coding: utf-8 -*-
"""
Created on Sat Dec 22 01:04:20 2018

@author: YinChao
"""
import pandas as pd
import get_price
from datetime import datetime
from datetime import timedelta
#import trade_day
#import get_k_day
global record
global invest_list #历史投资变量，全局变量

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
        
        header = ['deal_time','id','amount','price','direction']
        self.invest_list =pd.DataFrame(columns=header)
        today = datetime.now()
        try:
            start = datetime.strptime(start_day,'%Y%m%d')
            stop = datetime.strptime(stop_day,'%Y%m%d')
        except:
            for i in stop_day:
                if i == '-':
                    start = datetime.strptime(start_day,'%Y-%m-%d')
                    stop = datetime.strptime(stop_day,'%Y-%m-%d')
                    break
                elif i == '.':
                    start = datetime.strptime(start_day,'%Y.%m.%d')
                    stop = datetime.strptime(stop_day,'%Y.%m.%d')
                    break
                elif i == '/':
                    start = datetime.strptime(start_day,'%Y/%m/%d')
                    stop = datetime.strptime(stop_day,'%Y/%m/%d')
                    break
        if stop > today:
            stop = today
    #    print(today, start, stop)
        
        self.cur = start  
        self.stop = stop  
    def get_last_month_day(self):
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
        for day in self.get_last_month_day():
#            print(day)
            cnt = 3
            while cnt > 0:
                if 0 == trade_day.is_tradeday(day.strftime('%Y%m%d')):
                    day -= timedelta(1)
                    continue
#                file_name = 'sh'+self.id_list[0]+'.csv'
#                price = get_k_day.get_csv_price(file_name,day.strftime('%Y-%m-%d'))
                price = get_price.get_close_price(self.id_list[0], day.strftime('%Y%m%d'))
                price = float(price)
                if price > 0.1:
                    num_of_stock = int(self.money/price)
                    item = {'deal_time':day.strftime('%Y%m%d'), 
                            'id':self.id_list[0],
                            'amount':str(num_of_stock),
                            'price':str(price),
                            'direction':1}
                    self.invest_list = self.invest_list.append(item,ignore_index=True)
#                    print(day, price)
                    break
                else:
#                    break
#                    print(day)
                    day -= timedelta(1)
                cnt -= 1
        return self.invest_list
    
    def double_mode(self):
        for day in self.get_last_month_day():
#            print(day)
            cnt = 3
            while cnt > 0:
                if 0 == trade_day.is_tradeday(day.strftime('%Y%m%d')):
                    day -= timedelta(1)
                    continue
                price0 = float(get_price.get_close_price(self.id_list[0], day.strftime('%Y%m%d')))
                price1 = float(get_price.get_close_price(self.id_list[1], day.strftime('%Y%m%d')))
                if price1 > 0.1 and price0 > 0.1:
                    num_of_stock0 = int(self.money/2/price0)
                    num_of_stock1 = int(self.money/2/price1)
                    item = {'deal_time':day.strftime('%Y%m%d'), 
                            'id':self.id_list[0],
                            'amount':str(num_of_stock0),
                            'price':str(price0),
                            'direction':1}
                    self.invest_list = self.invest_list.append(item,ignore_index=True)
                    item = {'deal_time':day.strftime('%Y%m%d'), 
                            'id':self.id_list[1],
                            'amount':str(num_of_stock1),
                            'price':str(price1),
                            'direction':1}
                    self.invest_list = self.invest_list.append(item,ignore_index=True)
                    print(day, price0, price1)
                    break
                elif price0 < 0.1:
                    num_of_stock1 = int(self.money/price1)
                    item = {'deal_time':day.strftime('%Y%m%d'), 
                            'id':self.id_list[1],
                            'amount':str(num_of_stock1),
                            'price':str(price1),
                            'direction':1}
                    self.invest_list = self.invest_list.append(item,ignore_index=True)
                    print(day, price1)
                elif price1 < 0.1:
                    num_of_stock1 = int(self.money/price0)
                    item = {'deal_time':day.strftime('%Y%m%d'), 
                            'id':self.id_list[0],
                            'amount':str(num_of_stock0),
                            'price':str(price0),
                            'direction':1}
                    self.invest_list = self.invest_list.append(item,ignore_index=True)
                    print(day, price1)
                else:
#                    break
                    print('no record')
                    day -= timedelta(1)
                cnt -= 1
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