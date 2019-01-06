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

from datetime import datetime
from datetime import timedelta
import pandas as pd

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


    def InvestAnalyse(invest_list, start_day, stop_day):
        '''
        用户调用APP，输入投资历史和起止时间，得到(风险-年化收益率)，总成本、总股息收益、总资产
        输入：   投资列表->InvestRecord定义
                起止时间：必须是str格式，且固定为'20161003'格式！
        输出： 
        '''
        
        #1. 根据设定好的起止时间，结合投资历史，获得投资的起始时间并截取投资列表
        '''
        此处的逻辑比较复杂
        1. start_day比首条投资历史更久，直接将cur定到首条投资的当天
        2. start_day比首条投资历史晚，说明只是考察从中间某个时间的情况。此时需要截取投资历史
        3. stop_day比当前时间更晚，说明设置错误，强制将其置为当天
        4. stop_day比当前时间早，也比最后一条投资历史早，说明只考察某段投资历史
        '''
        print(invest_list)
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
                
        invest_pt = 0
        while invest_pt < len(invest_list): #截取投资列表
            invest_start = datetime.strptime(invest_list.iloc[invest_pt]['deal_time'],'%Y%m%d')
    #        print(invest_start)
            if start > invest_start:
                invest_pt += 1
            else:
                cur = invest_start
                break
            
        if stop > today:
            stop = today
            
        cur = invest_start
        print('step1: 实际起止时间：\n', 'start:',cur, ' --- stop:',stop,'\n')
        #此后cur代表今天，stop代表结束的那一天
            
        #2. 根据cur，直接向前搜索分红表，得到一个指针数组
        stock_id = [] #获取投资标的    
        ts_app = TushareApp.ts_app()
        for i in range(invest_pt, len(invest_list)):
            item = invest_list.iloc[i]['id']
            if item not in stock_id:
                stock_id.append(item)
        stock_len = len(stock_id)
        div_table = []   #获得相应的股息表
        for s in stock_id:
            tmp = ts_app.GetDividendTable(s)
            div_table.append(tmp)
            
        pt_div = [0]*len(stock_id) #获得股息的指针
        for i in range(stock_len):
            for j in range(len(div_table[i])):
                if cur > datetime.strptime(div_table[i].iloc[j]['除权日'],'%Y%m%d'):
    #                print(cur, div_table[i].iloc[j]['除权日'])
                    pass
                else:
                    pt_div[i] = j
                    break
        print('step2:根据分红表和cur，生成分红索引指针数组')        
    #    print(div_table)
        print('分红索引指针',pt_div,'\n')
        
        '''
        获得一个用于指示时间的列表,定义如下：
        day         type                id
        2017-09-10  dividend/buy        600660
        按时间排序
        数据类型定义：
        day:datetime， type：str  id：str
        备注：还有bug没有解！cur如果很靠后的话，结果不对——20181217
        '''
        index_column = ['day','type','id']
        time_index = pd.DataFrame(columns=index_column)
        
        for i in range(len(invest_list)): #投资记录
            tmp_day = datetime.strptime(invest_list.iloc[i]['deal_time'],'%Y%m%d')
            if cur > tmp_day:
                continue
            elif tmp_day > stop:
                break
            tmp_type = 'buy'
            tmp_id = invest_list.iloc[i]['id']
            tmp_dic = {'day':tmp_day, 'type':tmp_type, 'id':tmp_id}
            time_index = time_index.append(tmp_dic, ignore_index=True)
        
        first_exchange_day = time_index.iloc[0]['day'] 
        for i in range(stock_len): #分红记录
            for j in range(pt_div[i], len(div_table[i])):
                tmp_day = datetime.strptime(div_table[i].iloc[j]['除权日'],'%Y%m%d')
                if cur > tmp_day: #排除开始日期之前的分红记录
                    continue
                elif tmp_day < first_exchange_day:#交易第一天，排除之前的分红记录
                    continue
                elif tmp_day > stop:#排除停止时间之后的分红记录
                    break         
                tmp_type = 'dividend'
                tmp_id = stock_id[i]
                tmp_dic = {'day':tmp_day, 'type':tmp_type, 'id':tmp_id}
                time_index = time_index.append(tmp_dic, ignore_index=True)

    
    
        time_index = time_index.sort_values(by=['day'])
        time_index.index = pd.Index(range(len(time_index)))
        print('step3:获得一个时间指示表time_index，用于快速索引日期')
    #    print(time_index,'\n')
        
        # 循环直到结束，统计收益率和风险
        '''
        根据time_index,cur,stop三个参数，开始每天循环检查
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
        
        print('step4:具体执行交易和分红记录')
        i = 0 #time_index的索引
        excute_time = len(time_index)
    #    print('共有%d条记录'%excute_time,'\n')
        yesterday = cur
        year_asset = [] #年度资产数据，用于计算波动率
        while cur < stop and i < excute_time:
            
            #年度数据统计，用于计算风险系数   
            if yesterday.year != cur.year:
                year_asset.append(stock_num.copy())
    #            print(yesterday)
    #            total = 0
    #            for key in stock_num:
    #                str_id = key
    #                num = stock_num[key]
    #                try:
    #                    price, day = get_price.get_price(str_id,yesterday)
    #                    asset = price * num
    #                    year_asset.append(asset)
    #                except:
    #                    print('miss ', key, '\'s price')
    #                    pass
                
            if cur == time_index.iloc[i]['day']:
                if time_index.iloc[i]['type'] == 'buy': #买卖记录
                    for s in stock_id:
                        if time_index.iloc[i]['id'] == s:
                            cur_id = s
                    quant = int(invest_list.iloc[invest_pt]['amount']) * int(invest_list.iloc[invest_pt]['direction'])
                    stock_num[cur_id] += quant #交易的股票数
                    cost += float(invest_list.iloc[invest_pt]['price']) * quant
    #                print('交易记录%d：'%i,cur)
    #                print(cur_id, '增加了：',quant,'股','单价：',float(invest_list.iloc[invest_pt]['price']))
    #                print('\n\n')
                    
                    
                    
                    invest_pt += 1 #指向下一条投资记录
                    i += 1 #指向下一个处理点（此处要判断是否到年尾了）
                    
                elif time_index.iloc[i]['type'] == 'dividend': #分红记录
                    for s in range(len(stock_id)):
                        if time_index.iloc[i]['id'] == stock_id[s]:
                            cur_id = s
                    #第几个股要分红
                    cur_stock = stock_id[cur_id] #找出当前是那个股要分红了
                    index = pt_div[cur_id] #分红列表的索引值
                    item_tmp = div_table[cur_id].iloc[index]
                    add_earn = stock_num[cur_stock] * float(item_tmp['派息'])
                    ultra_earn += stock_num[cur_stock] * float(item_tmp['派息'])
                    add_stock = stock_num[cur_stock] * (float(item_tmp['转股']) + float(item_tmp['送股']))
                    
#                    print('分红记录%d'%i, cur_stock)
#                    print(item_tmp)
#                    print('股份数：',stock_num[cur_stock],'，股本增加：',add_stock,'分红：',add_earn)
#                    print('\n\n')
                    stock_num[cur_stock] += stock_num[cur_stock] * (float(item_tmp['转股']) + float(item_tmp['送股']))
                    
                    pt_div[cur_id] += 1  #分红表索引加一
                    i+=1
                 
            yesterday = cur
            
            cur += timedelta(1)
        if yesterday + timedelta(1) <= cur: #防止截止日期刚好是一年的最后一天，重复计算
            year_asset.append(stock_num.copy())
        
        
        print('step5:收益统计')
        total_asset = 0
        for key in stock_num:
            str_id = key
            num = stock_num[key]
            print(str_id, num)
            try:
                price, day= ts_app.GetPrice(str_id)
                asset = price * num
                total_asset += asset
            except:
                pass
        print('成本:', round(cost,2), '期末资产：', round(total_asset,2), '额外分红：',ultra_earn)
        total_rate = round((total_asset - cost)/cost, 4)
        per_rate = round(total_rate / (cur.year - invest_start.year),4)
        print('总收益率：',total_rate,'，年均复合增长率：',per_rate)
    
        
        return year_asset






if __name__ == '__main__':
    stock_list = ['600660','601012','000651','600522']
    test = algorithm()
    a, b = test.GetAdvise(10000, stock_list)
    print(a, b)