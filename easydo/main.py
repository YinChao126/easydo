# -*- coding: utf-8 -*-
"""
Created on Thu Dec 27 22:00:36 2018

@author: yinchao
本文件用于大量回测，探索股债比的有效性
"""
import Data.TushareApp as TushareApp

import User.user
import Algorithm.algorithm as alg

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

    #测试：获得股票估值水平
    app = TushareApp.ts_app()
    test = alg.algorithm.Estimation('601012.SH',0.15)
    
#    test = User.user.cUser('sss', '123')
#    test.Login('s', 'a')
#
#    adv = alg.algorithm()
#    stock_list = ['600660', '601012', '000651', '600522']
#    a, b = adv.GetAdvise(10000, stock_list)
#    print(a, b)
