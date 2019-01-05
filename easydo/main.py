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
    app = TushareApp.ts_app()
    a,b,c = app.GetAvgInfo(id_str[0], 1)
    print(a,b,c)
        
    tbl = app.GetFinanceTable('000651.SZ',6)
    print(tbl)

#    test = alg.algorithm.Estimation('600660.SH',0.3,1)
    
#    test = User.user.cUser('sss', '123')
#    test.Login('s', 'a')
#
#    adv = alg.algorithm()
#    stock_list = ['600660', '601012', '000651', '600522']
#    a, b = adv.GetAdvise(10000, stock_list)
#    print(a, b)
