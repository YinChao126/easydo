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
        ts_app = TushareApp.ts_app()
        eps = 0.72 #去年除非每股收益，财报爬取即可
        tbl = ts_app.GetFinanceTable(ID,1)
        eps = tbl.iloc[-1]['dt_eps']
        if not eps: #如果没有除非eps，则用eps代替
            eps = tbl.iloc[-1]['eps']
        avg_growth = ts_app.AvgGrowthInfo(ID,5)#过去5年eps平均增长率，财报爬取
        turnover, avg_pe, avg_pb = ts_app.AvgExchangeInfo(ID, 3)#过去3年平均PE、换手率
        
        basic = ts_app.BasicInfo(ID) #最近收盘的基本情况
        cur_pe= basic.iloc[-1]['pe']
        cur_price = basic.iloc[-1]['close']
#        print(basic)
        
        #成长型股票PE修正
        if avg_growth > 0.5: #50%以上算高增长，PE打6折，此时的PE不靠谱！
            avg_pe *= 0.6
        elif avg_growth > 0.3: #30%以上算中高速增长，PE打8折
            avg_pe *= 0.8
        elif avg_growth > 0.15: #15%以上算中速,PE打9折
            avg_pe *= 0.9

        #2.中间变量计算
        '''
        1.计算增长率：过去5年的平均增长率和预测的今年增长率加权
        2.根据平均5年pe_ttm的水平结合现价，得到预测的价格
        3.根据现价和预测价格推测出溢价水平
        '''
        
        confidence = 0.2 + confidence * 0.6#实际权值范围[0.2-0.8]，防止过分自信和悲观
        growth = avg_growth * (1-confidence) + est_growth * confidence
        est_price = cur_price / cur_pe * avg_pe * (1+growth)
        overflow_rate = (cur_price - est_price) / est_price
        
        print('平均PE:',avg_pe,'平均增长率：',avg_growth,'增长率加权:',round(growth,4))
        print('现价:',cur_price,'年末估计值：',est_price)
        
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
        
        print('参考溢价等级：',flow_level)
        return est_price, flow_level

if __name__ == '__main__':
    stock_list = ['600660','601012','000651','600522']
    test = algorithm()
    a, b = test.GetAdvise(10000, stock_list)
    print(a, b)