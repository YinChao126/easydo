# -*- coding: utf-8 -*-
"""
Created on Thu Dec 27 22:00:36 2018

@author: yinchao
本文件用于大量回测，探索股债比的有效性
"""
import os,sys
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OTHER_DIR = BASE_DIR + r'\Data'
sys.path.append(OTHER_DIR)
OTHER_DIR = BASE_DIR + r'\Algorithm'
sys.path.append(OTHER_DIR)
OTHER_DIR = BASE_DIR + r'\Miscellaneous'
sys.path.append(OTHER_DIR)
OTHER_DIR = BASE_DIR + r'\Mysql'
sys.path.append(OTHER_DIR)
OTHER_DIR = BASE_DIR + r'\User'
sys.path.append(OTHER_DIR)
OTHER_DIR = BASE_DIR + r'\Debug'
sys.path.append(OTHER_DIR)

import Data.TushareApp as TushareApp

import User.user
import Algorithm.algorithm as alg

if __name__ == '__main__':
    id_str = ['000651.SZ', '002597.SZ','600377.SH','600660.SH','601012.SH']
    app = TushareApp.ts_app()
    for s in id_str:
        app.update(s,2)   
    tbl = app.GetFinanceTable('000651.SZ',6)
    print(tbl)
    
#    test = User.user.cUser('sss', '123')
#    test.Login('s', 'a')
#
#    adv = alg.algorithm()
#    stock_list = ['600660', '601012', '000651', '600522']
#    a, b = adv.GetAdvise(10000, stock_list)
#    print(a, b)
