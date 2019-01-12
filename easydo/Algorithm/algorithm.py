import os,sys
import pandas as pd
import requests
from datetime import datetime
from datetime import timedelta
import pandas as pd

BASE_DIR=os.path.dirname(os.path.dirname(sys.argv[0]))
sys.path.append(BASE_DIR)

import Algorithm.stock_bond_rate as stock_bond_rate
import Miscellaneous.TimeConverter as TimeConverter
import Data.TushareApp as TushareApp

class algorithm:

    def __init__(self):
        self.ts_app = TushareApp.ts_app()

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
    
    def Estimation(self, ID, est_growth, confidence=0.5):
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
        avg_growth = ts_app.AvgGrowthInfo(ID,5)#过去5年eps平均增长率，财报爬取       
        turnover, avg_pe, avg_pb = ts_app.AvgExchangeInfo(ID, 3)#过去3年平均PE、换手率
        basic = ts_app.BasicInfo(ID) #最近收盘的基本情况
        cur_pe= basic.iloc[-1]['pe']
        cur_pe_ttm= basic.iloc[-1]['pe_ttm']
        cur_price = basic.iloc[-1]['close']
        cur_eps = cur_price / cur_pe
        print('当前水平：(price, pe, pe_ttm):',cur_price,cur_pe,cur_pe_ttm)
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
        growth = round(avg_growth * (1-confidence) + est_growth * confidence, 4)
        est_price_growth = cur_price / cur_pe * avg_pe * (1+growth)
        est_price_pe = cur_eps * avg_pe
        est_price = est_price_pe
        print('平均PE:',avg_pe,'平均增长率：',avg_growth,'增长率加权:',growth)
        print('估值定义：增长估值指根据已有增长形势估计年末的估价，现价估值指当前价格估计')
        print('现价:',cur_price,'增长估值：',round(est_price_growth,2),'现价估值：',round(est_price_pe,2))
        if est_price_growth < est_price_pe:
            est_price = est_price_growth
        overflow_rate = (cur_price - est_price) / est_price
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


    def InvestAnalyse(self, invest_list, start_day, stop_day = 0):
        '''
        @描述：用户调用APP，输入投资历史和起止时间，得到(风险-年化收益率)，总成本、总股息收
              益、总资产
        @输入：   投资列表->InvestRecord定义，必须是list类型
                起止时间：必须是str格式，且固定为'20161003'格式！
                stop_day如果不填，默认是今天
        @输出：投资收益率
        @备注：风险波动率还没有实现
        '''
###############################################################################
        '''
        1. 起始时间确定： start/stop/ cur(首条投资时间)
        此处的逻辑比较复杂
        1. start_day比首条投资历史更久，直接将cur定到首条投资的当天
        2. start_day比首条投资历史晚，说明只是考察从中间某个时间的情况。此时需要截取投资历史
        3. stop_day比当前时间更晚，说明设置错误，强制将其置为当天
        4. stop_day比当前时间早，也比最后一条投资历史早，说明只考察某段投资历史
        '''
        today = datetime.now()
        start = TimeConverter.str2dtime(start_day)
        try:
            stop = TimeConverter.str2dtime(stop_day)
            if stop > today:
                stop = today
        except:
            stop = today
        invest_tbl = invest_list[invest_list.deal_time >= TimeConverter.dtime2str(start)]
        if invest_tbl.empty == True:
            print('没有投资记录')
            return
        invest_tbl.index = range(len(invest_tbl))
        cur = TimeConverter.str2dtime(invest_tbl.loc[0,'deal_time'])
#        print('step1: 实际起止时间：\n', 'start:',cur, ' --- stop:',stop,'\n')
#        print('step2: 截取invest_list')
#        print(invest_tbl)

###############################################################################
        '''
        根据起始时间和目标个股，得到一个分红总表div_tbl并按时间顺序排列
        '''
        stock_id = [] #获取投资标的    
        ts_app = TushareApp.ts_app()
        for i in range(len(invest_tbl)):
            item = invest_tbl.iloc[i]['id']
            if item not in stock_id:
                stock_id.append(item)
        stock_len = len(stock_id)
        div_tbl = []   #获得相应的股息表
        div_tbl = pd.DataFrame(columns=['名称','年度','派息','转股','送股','除权日'])
        for s in stock_id:
            tmp = ts_app.GetDividendTable(s)
            tbl = tmp[(tmp.除权日 >= TimeConverter.dtime2str(cur)) & (tmp.除权日 <= TimeConverter.dtime2str(stop))]
            div_tbl = pd.concat([div_tbl,tbl])
        div_tbl = div_tbl.sort_values(by=['除权日'])
        div_tbl.index = range(len(div_tbl))
#        print('\nstep3:获得个股名单，并根据分红表和cur，合成分红表')
#        print('个股名单：',stock_id)
#        print(div_tbl)

###############################################################################    
        '''
        根据投资列表和分红表，获得一个用于实际执行的时间列表ex_tbl,定义如下：
        day         type                id
        2017-09-10  dividend/buy        600660.SH
        按时间排序
        数据类型定义：
        day:datetime， type：str  id：str
        '''
        index_column = ['day','type','id']
        ex_tbl = pd.DataFrame(columns=index_column) #执行列表
        for i in range(len(invest_tbl)):
            tmp_day = TimeConverter.str2dtime(invest_tbl.iloc[i]['deal_time'])
            tmp_id = invest_tbl.iloc[i]['id']
            tmp_type = 'buy'
            tmp_dic = {'day':tmp_day, 'type':tmp_type, 'id':tmp_id}
            ex_tbl = ex_tbl.append(tmp_dic, ignore_index=True)
        for i in range(len(div_tbl)):
            tmp_day = TimeConverter.str2dtime(div_tbl.iloc[i]['除权日'])
            tmp_id = div_tbl.iloc[i]['名称']
            tmp_type = 'div'
            tmp_dic = {'day':tmp_day, 'type':tmp_type, 'id':tmp_id}
            ex_tbl = ex_tbl.append(tmp_dic, ignore_index=True)
        ex_tbl = ex_tbl.sort_values(by=['day'])
        ex_tbl.index = range(len(ex_tbl))
#        print('\nstep4:获得一个按时间顺序执行表ex_tbl，用于快速索引日期')
#        print(ex_tbl)

###############################################################################
        '''
        根据ex_tbl,cur,stop三个参数，开始每天循环检查
        为所有的股票设置一个stock_num[]，设置一个总的cost，asset，ultra_earn参数
        最终输出年度的asset列表（用于计算风险），cost和ultra_earn计算投资收益率和股息率
        
        先判断type，然后判断id
        '''    
        stock_num = []#建立一个字典，用于存储个股的数量
        cost = 0 #总成本
        ultra_earn = 0 #总分红
        asset = [0] #年末资产总计
        for s in stock_id:
            a = (s, 0)
            stock_num.append(a)
        stock_num = dict(stock_num) 
        excute_time = len(ex_tbl)
        yesterday = cur
        year_asset = [] #年度资产数据，用于计算波动率
        buy_id = 0
        div_id = 0
        for i in range(len(ex_tbl)):
            if ex_tbl.iloc[i]['type'] == 'buy':
                for s in stock_id:
                    if ex_tbl.iloc[i]['id'] == s:
                        cur_id = s
                quant = int(invest_tbl.iloc[buy_id]['amount']) * int(invest_tbl.iloc[buy_id]['direction'])
                stock_num[cur_id] += quant #交易的股票数
                cost += float(invest_tbl.iloc[buy_id]['price']) * quant
#                print('交易记录%d：'%i,cur)
#                print(cur_id, '增加了：',quant,'股','单价：',float(invest_tbl.iloc[buy_id]['price']))
#                print('\n\n')
                buy_id += 1
            else:
                for s in range(len(stock_id)):
                    if ex_tbl.iloc[i]['id'] == stock_id[s]:
                        cur_id = s
                #第几个股要分红
                cur_stock = stock_id[cur_id] #找出当前是那个股要分红了
                
                item_tmp = div_tbl.iloc[div_id]

                add_earn = stock_num[cur_stock] * float(item_tmp['派息'])
                ultra_earn += stock_num[cur_stock] * float(item_tmp['派息'])
                add_stock = stock_num[cur_stock] * (float(item_tmp['转股']) + float(item_tmp['送股']))
                stock_num[cur_stock] += add_stock
#                print('分红记录%d'%i, cur_stock)
#                print(item_tmp)
#                print('股份数：',stock_num[cur_stock],'，股本增加：',add_stock,'分红：',add_earn)
#                print('\n\n')
                div_id += 1
               
        print('\nstep5:交易结果')
        print('到期股份数:',stock_num)
        
###############################################################################
        total_asset = 0
        for key in stock_num:
            str_id = key
            num = stock_num[key]
            last_day = TimeConverter.dtime2str(stop)
            price, day= ts_app.GetPrice(str_id, last_day)
            asset = price * num
            total_asset += asset
            
        total_rate = round((total_asset - cost)/cost, 4)
        per_rate = round(total_rate / (stop.year - cur.year+1),4)
        print('\nstep6:收益统计')
        print('成本:', round(cost,2), '期末资产：', round(total_asset,2), '额外分红：',ultra_earn)
        print('总收益率：',total_rate,'，年均复合增长率：',per_rate)
        return year_asset






if __name__ == '__main__':
    stock_list = ['600660','601012','000651','600522']
    test = algorithm()
    a, b = test.GetAdvise(10000, stock_list)
    print(a, b)