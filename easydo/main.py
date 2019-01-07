# -*- coding: utf-8 -*-
"""
Created on Thu Dec 27 22:00:36 2018

@author: yinchao
本文件用于大量回测，探索股债比的有效性
"""
import Data.TushareApp as TushareApp
import Algorithm.algorithm as alg
import Algorithm.strategy_generator as stg

if __name__ == '__main__':
    id_str = ['000651.SZ', '002597.SZ','600377.SH','600660.SH','601012.SH']
    
#    #测试：获得个股连续n年平均交易水平（换手率，pe_ttm,pb）
#    app = TushareApp.ts_app()
#    a,b,c = app.AvgExchangeInfo(id_str[0], 1)
#    print(a,b,c)
    
#    #测试：获得个股连续n年的财务统计数据
#    app = TushareApp.ts_app()
#    tbl = app.GetFinanceTable('000651.SZ',6)
#    print(tbl)

#    #测试：获得股票估值水平
#    app = TushareApp.ts_app()
#    test = alg.algorithm()
#    test.Estimation(id_str[-1], 0.0, 1)
    
#    #测试：获得个股前一天的基本情况
#    app = TushareApp.ts_app()
#    test = app.BasicInfo('600377.SH')

#    #测试：获得指定个股的分红表
#    app = TushareApp.ts_app()
#    out = app.GetDividendTable(id_str[0])
    
    #测试：根据投资列表求得投资收益率
    start_day = '20100101'
    stop_day = '20181224'
    invest_list = stg.create_test_invest_list()
    a = alg.algorithm()
    a.InvestAnalyse(invest_list,start_day,stop_day)

#    #测试：生成策略
#    stock_list = ['600522.SH','601012.SH']
#    invest_money = 10000
#    start = '20180101'
#    stop = '20181231'
#    a = stg.InvestRecordGenerator(stock_list,invest_money,start,stop)
##    invest_list = a.single_mode()
#    invest_list = a.double_mode()
#    print(invest_list)
    
#    #测试，用户登录    
#    test = User.user.cUser('sss', '123')
#    test.Login('s', 'a')
