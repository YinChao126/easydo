import os,sys
import pandas as pd
import requests

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OTHER_DIR = BASE_DIR + r'\Algorithm'
sys.path.append(OTHER_DIR)
OTHER_DIR = BASE_DIR + r'\Miscellaneous'
sys.path.append(OTHER_DIR)
OTHER_DIR = BASE_DIR + r'\Data'
sys.path.append(OTHER_DIR)

import stock_bond_rate
from Miscellaneous import TimeConverter
from Data import TushareApp

class algorithm:

    def __init__(self):
        self.test = 0

    def GetAdvise(self, money, stock_list):
        '''
        对外输出API：输出投资建议
        输入：投资额， 目标个股
        输出：股票投资比率， 建议重点投资的股票组合
        '''
        # cur_workspace = os.getcwd()
        # sys.path.append(cur_workspace+'\Algorithm')
        # print(os.getcwd())
        # import stock_bond_rate

        rate = stock_bond_rate.GetStockRate() #获取股债比
        advise_list = stock_list[:2]
        stock_money = money * rate
        print('you should invest %d to stock' % stock_money)
        return rate, advise_list
    
    def Estimation(ID, est_growth, confidence=0.5):
        '''
        更新：2018-12-31
        描述：输入ID和增长率手算值，自动得到目标价和溢价比率，提供投资建议
        输入：
        @ID(str)->个股ID号
        @est_growth(float)[0~1]->手动预测今年的增长率
        @confidence(float)[0~1]->计算结果的不确定度[0-1]，越是可预测的，confidence越高
        输出：无
        返回值：
        @ est_price(float)-> 年底目标价
        @ flow_level(int) -> 溢价等级[-3,3],详见下文的溢价表定义
        '''
        #1.参数输入
        avg_pe = 15.2 #十年平均除非市盈率，通过乌龟量化爬取，或者直接通过财报计算得来
        eps = 3.72 #去年除非每股收益，财报爬取即可
        avg_growth = 0.2#过去5年eps平均增长率，财报爬取
        ts_app = TushareApp.ts_app()
        cur_price = ts_app.GetPrice(ID) #现价，直接爬取
        
        
        
        #2.中间变量计算
        confidence = 0.2 + confidence * 0.6#实际权值范围[0.2-0.8]，防止过分自信和悲观
        print(confidence)
        growth = avg_growth * (1-confidence) + est_growth * confidence
        print(growth)
        est_eps = eps * (1+growth)
        est_price = est_eps * avg_pe
        print(est_price)
        
        '''
        市值表现核对，估值溢价计算与投资建议
        溢价定义：
        [ >  0.20] 绝对高估，  【空仓】
        [ 0.10 ~ 0.20]明显高估 【停止增持->减仓】
        [ 0.05 ~ 0.10]略高估， 【谨慎增持->停止增持】
        [-0.05 ~ 0.05]正常    【正常定投】
        [-0.10 ~-0.05]略低估， 【开始增持】
        [-0.20 ~-0.10]明显低估 【大幅增持】
        [ ~ -0.20] 绝对低估，  【满仓】
        返回值表示：溢价水平[-3,-2,-1,0,1,2,3]从低估到高估排列
        '''  
        overflow_rate = (cur_price - est_price) / est_price
    #    print(overflow_rate)
        
        flow_level = 0 #溢价水平
        if overflow_rate > 0.2:
            flow_level = 3
        elif overflow_rate > 0.1 and overflow_rate <= 0.2:
            flow_level = 2
        elif overflow_rate > 0.05 and overflow_rate <= 0.1:
            flow_level = 1
        elif overflow_rate > -0.05 and overflow_rate <= 0.05:
            flow_level = 0
        elif overflow_rate > -0.1 and overflow_rate <= -0.05:
            flow_level = -1
        elif overflow_rate > -0.2 and overflow_rate <= -0.1:
            flow_level = -2
        else:
            flow_level = -3
        
        print(flow_level)
        return est_price, flow_level

if __name__ == '__main__':
    stock_list = ['600660','601012','000651','600522']
    test = algorithm()
    a, b = test.GetAdvise(10000, stock_list)
    print(a, b)