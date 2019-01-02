# -*- coding: utf-8 -*-
'''
文档说明

list 对照表
0   总资产
1   净资产
2   资产负债比
3   流动资产
4   一年内到期的长期负债
5   应收账款
6   预收账款
7   存货

8   营业收入
9   营业成本
10  营业税金及附加
11  财务费用
12  营业外收入
13  净利润
14  除非净利润
15  每股收益

16  经营净额
17  投资净额
18  筹资净额
19  汇率影响
20  现金净增加额
21  期末现金余额

22  流动比率
23  资产周转率
24  存货周转率

25  总市值/净资
26  市盈率
27  市净率
28  名义净资产收益率
29  真实净资产收益率
30  毛利率
31  营收增长率
32  除非净利润增长率
'''
import sys
sys.path.append('../..')
import get_price
import get_dividends_history
from datetime import datetime, timedelta
import pandas as pd
import tushare as ts
import re
import urllib.request
import numpy as np
np.set_printoptions(suppress=True)
import Config
import trade_day
import csv
import os


def DataTreat(AStr):
    AStr = str(AStr)
    flag = AStr.find(',')
    if (flag == -1):
        returnNum = float(AStr)
    else:
        returnNum = float(AStr.replace(',', ''))
    return returnNum


BasePath = '.\\easydo\\Algorithm\\M1809'
hstPath = os.path.join(BasePath, "history_data")  # 历史数据路径


class GetData:
    def __init__(self, DataSource='SQL', HstPath=hstPath):
        if (DataSource == 'CSV' or DataSource == 'csv'):
            self.DataSource = 'CSV'
        else:
            self.DataSource = 'SQL'
        self.HstPath = HstPath
        pass

    # def GetSingleItem(self, stock_id, year):
    # '''
    # 返回一个series
    # '''
    #     p_len = len(Config.parameter) #自动计算参数列表长度
    #     info = []   #实际待填充的字段，最后用于生成Series的value部分

    #     for s in range(p_len):
    #         info.append(-1) #初始化为-1，代表还未填充

    #     #资产负债表中查询与填充
    #     cmd = "select * from zichanfuzhai where h79 = \'"+stock_id+"\' and h80 = \'"+str(year)+"-12-31\';"
    #     Config.cur.execute(cmd)
    #     result = Config.cur.fetchall()
    # #    print(result)
    #     result = list(result[0])
    # #    print(result)
    #     # 此处需要把 -- 的选项替换成 0
    #     for i in range(len(result)):
    #         if result[i] == '--':
    #             result[i] = '0'
    #     data1 = result #获得资产负债表信息
    #     info[0] = DataTreat(data1[37]) #总资产
    #     debt = DataTreat(data1[65]) #总负债
    #     info[2] = round((debt / info[0]),2)     #资产负债比
    #     info[1] = info[0] - debt #净资产
    #     info[3] = DataTreat(data1[16]) #流动资产
    #     info[4] = DataTreat(data1[52]) #一年内到期的长期负债
    #     info[5] = DataTreat(data1[4])  #应收账款
    #     info[6] = DataTreat(data1[42])  #预收账款
    #     info[7] = DataTreat(data1[10])  #存货
    #     CurrentLiabilities = DataTreat(data1[54])  #流动负载
    #     #去年的资产负载表
    #     cmd = "select * from zichanfuzhai where h79 = \'"+stock_id+"\' and h80 = \'"+str(year-1)+"-12-31\';"
    #     Config.cur.execute(cmd)
    #     result = Config.cur.fetchall()
    #     data1_last = list(result[0]) #获得去年年末资产负债表信息
    #     # 此处需要把 -- 的选项替换成 0
    #     for i in range(len(data1_last)):
    #         if data1_last[i] == '--':
    #             data1_last[i] = '0'
    #     AssetLastYear = DataTreat(data1_last[37]) #总资产
    #     InventoryLastYear = DataTreat(data1_last[10])  #去年存货

    #     #利润表查询与填充
    #     cmd = "select * from Profit where h29 = \'"+stock_id+"\' and h30 = \'"+str(year)+"-12-31\';"
    #     Config.cur.execute(cmd)
    #     result = Config.cur.fetchall()
    #     result = list(result[0])
    #     # 此处需要把 -- 的选项替换成 0
    #     for i in range(len(result)):
    #         if result[i] == '--':
    #             result[i] = '0'
    #     data2 = result #获得资产负债表信息
    # #    print(data)
    #     info[8] = DataTreat(data2[0])  #营业收入
    #     info[9] = DataTreat(data2[2])  #营业总成本
    #     info[10] = DataTreat(data2[4])  #营业税金及附加
    #     info[11] = DataTreat(data2[7])  #财务费用
    #     LossFromAssetDevaluation = DataTreat(data2[8])  #资产减值损失
    #     IncomeFromInvestment = DataTreat(data2[10]) #投资收益
    #     info[12] = DataTreat(data2[14])  #营业外收入
    #     NonbusinessExpenditure = DataTreat(data2[15])  #营业外支出
    #     info[13] = DataTreat(data2[19])  #净利润

    #     #非经常性盈利损失（此处只计算了前4项，会对计算除非净利润带来不准确）
    #     NonRecurringProfitAndLoss = info[12] - NonbusinessExpenditure + IncomeFromInvestment - LossFromAssetDevaluation
    #     #除非净利润=净利润-非经常性盈利损失
    #     info[14] = info[13] - NonRecurringProfitAndLoss  #除非净利润
    #     info[15] = DataTreat(data2[22])  #每股收益
    #     stock_num = info[13]/ info[15] #股份数量
    #     #上一年度利润表
    #     cmd = "select * from Profit where h29 = \'"+stock_id+"\' and h30 = \'"+str(year-1)+"-12-31\';"
    #     Config.cur.execute(cmd)
    #     result = Config.cur.fetchall()
    #     data2_last = list(result[0]) #获得资产负债表信息
    #     # 此处需要把 -- 的选项替换成 0
    #     for i in range(len(data2_last)):
    #         if data2_last[i] == '--':
    #             data2_last[i] = '0'

    #     RevenueLast = DataTreat(data2_last[1])  #营业收入
    #     NonbusinessIncomeLast = DataTreat(data2_last[14])  #营业外收入
    #     IncomeFromInvestmentLast = DataTreat(data2_last[10]) #投资收益
    #     NonbusinessExpenditureLast = DataTreat(data2_last[15])  #营业外支出
    #     LossFromAssetDevaluationLast = DataTreat(data2_last[8])  #资产减值损失
    #     NonRecurringProfitAndLossLast = NonbusinessIncomeLast + IncomeFromInvestmentLast - NonbusinessExpenditureLast - LossFromAssetDevaluationLast
    #     NetProfit = DataTreat(data2_last[19])  #净利润
    #     NullNetProfit = NetProfit - NonRecurringProfitAndLossLast

    #     #现金流量表查询与填充
    #     cmd = "select * from cashFlow where h72 = \'"+stock_id+"\' and h73 = \'"+str(year)+"-12-31\';"
    #     Config.cur.execute(cmd)
    #     result = Config.cur.fetchall()
    #     result = list(result[0])
    #     # 此处需要把 -- 的选项替换成 0
    #     for i in range(len(result)):
    #         if result[i] == '--':
    #             result[i] = '0'
    #     data3 = result #获得资产负债表信息
    #     info[16] = DataTreat(data3[9]) #经营净额
    #     info[17] = DataTreat(data3[21]) #投资净额
    #     info[18] = DataTreat(data3[33]) #筹资净额
    #     info[19] = DataTreat(data3[34]) #汇率影响

    #     #现金净增加额=现金的期末余额-现金的期初余额
    #     info[20] = DataTreat(data3[67]) - DataTreat(data3[66])  #现金净增加额
    #     info[21] = DataTreat(data3[67]) #期末现金余额

    #     #指标计算，可能还需要获取额外的数据如实时股价等。。。

    #     #流动比率＝流动资产（3）/流动负债（h55）x100%
    #     info[22] = round(info[3] / CurrentLiabilities,2) #流动比率

    #     #资金周转率=本期销售收入净额（营业收入）*2/（资产总额期初余额+资产总额期末余额），期末期初按一年计算
    #     info[23] = round(info[8] * 2 / (info[0] + AssetLastYear),2)

    #     #存货周转率 = 营业成本 / 平均存货 ，平均存货=（期初存贷余额+期末存贷余额)/2,按一年期进行计算
    #     info[24] = round(info[9] * 2 / (info[7] + InventoryLastYear),2)

    #     #tushare实时数据
    #     '''
    #     per:市盈率
    #     pb:市净率
    #     mktcap:总市值
    #     nmc:流通市值
    #     '''
    #     DatStr = datetime(year,12,31)
    #     cnt = 30 #考察连续30个交易日是否有数据
    #     while cnt > 0: #获取年尾的数据，排除节假日，停牌的情况.无法排除未上市的情况
    #         day = DatStr.strftime('%Y%m%d')
    #         if trade_day.is_tradeday(day):
    #             cnt -= 1
    #             cur_price= DataTreat(str(get_price.get_close_price(stock_id,day)))
    #             if cur_price > 0.1:
    # #                print(day)
    # #                print(cur_price)
    #                 break
    #         DatStr -= timedelta(1)
    #     if cnt <= 0: #连续60个交易日无数据，说明该公司长期停牌
    #         cur_price = 0
    #         print('warning,',year, ',',stock_id,'has no data' )
    # #    print (cur_price)
    # #    print (date)

    #     info[25] = round(cur_price * stock_num / info[1],2)
    #     info[26] = round(cur_price / info[15],2) #静态市盈率
    #     info[27] = round(info[1] / stock_num,2) #市净率

    # #    DataTushare =  (ts.get_today_all().values)[0]
    # #    per = DataTushare[11]
    # #    pb = DataTushare[12]
    # #    mktcap = DataTushare[13]
    # #    info[25] =  round(mktcap / info[1],2) #总市值/净资
    # #    info[26] =  per #市盈率
    # #    info[27] = pb #市净率

    #     #真实净资产收益率 = 净利润 * 2 / (本年期初净资产+本年期末净资产)
    #     NetAssetEnd = info[0] - debt
    #     NetAssetBegin = DataTreat(data1_last[37]) - DataTreat(data1_last[65])
    #     info[29] = round(info[13] * 2 / (NetAssetEnd + NetAssetBegin),2)
    #     #名义净资产收益率 = 真实净资产收益率 * 市净率
    #     info[28] = round(info[29] * info[27],2)

    # #    #毛利率 = （营业收入 - 营业成本） / 营业成本 * 100%
    #     info[30] = round((info[8] - info[9]) / info[9],2)

    # #    #营收增长率 = (本年度营业收入 - 上年度营业收入) /上年度营业收入 *100%
    #     info[31] = round((info[8] - RevenueLast) / RevenueLast,2)
    # #
    # #    #除非净利润增长率 = (年末 - 年初)/ 年初 * 100%
    #     info[32] = round((info[14] - NullNetProfit) / NullNetProfit,2)

    #     px,Date=get_dividends_history.get_px_single_year(stock_id,year-1)
    #     if px == 0.0 or Date == '--':
    #         info[33] = 0
    #     else:
    #         DatStr = datetime.strptime(Date, '%Y%m%d')
    #         cnt = 30 #考察连续30个交易日是否有数据
    #         while cnt > 0: #获取年尾的数据，排除节假日，停牌的情况.无法排除未上市的情况
    #             day = DatStr.strftime('%Y%m%d')
    #     #        print(day)
    #             if trade_day.is_tradeday(day):
    #                 cnt -= 1
    #                 cur_price = float(get_price.get_close_price(str(stock_id),day))
    #                 if cur_price > 0.1:
    #                     info[33] = round(float(px) / 10 / float(cur_price),3)
    #                     break
    #             DatStr -= timedelta(1)
    # #    info[33] = round(float(px) / 10 / float(cur_price),3)
    #     info[34] = round(float(px) / 10 / info[15],3)
    #     #print(pd.Series(info,index = para))
    #     return pd.Series(info,index = Config.parameter)

    def GetSingleLocalItem(self, stock_id, year, quarter=4):
        if quarter == 1:
            #        time_str = datetime(year, 3,31)
            time_str = str(year) + '-03-31'
        elif quarter == 2:
            #        time_str = datetime(year, 6,30)
            time_str = str(year) + '-06-30'
        elif quarter == 3:
            #        time_str = datetime(year, 9,30)
            time_str = str(year) + '-09-30'
        elif quarter == 4:
            #        time_str = datetime(year, 12,31)
            time_str = str(year) + '-12-31'
        else:
            time_str = str(year) + '-12-31'
        time_str_last_year = str(year - 1) + '-12-31'

        prefix = self.HstPath + '\\'
        suffix_balnce_sheet = '_balance_sheet.csv'
        suffix_cash_flow = '_cash_flow.csv'
        suffix_profit = '_profit.csv'
        with open(
                prefix + stock_id + suffix_balnce_sheet, 'r',
                encoding='gbk') as csvfile:
            csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
            head_parameter = next(csv_reader)  # 读取第一行每一列的标题
            while True:
                try:
                    data = next(csv_reader)  # 读取第一行每一列的标题
                    if data[0] == time_str_last_year:  #获取去年的年报信息
                        result_last = data
                    if data[0] == time_str:  #获取当前的待查询的信息
                        result = data
                        break
                except Exception as e:
                    print('except:', e)
                    break
        try:
            trash = result_last
        except Exception as e:
            print('except:', e)
            print('没有前一年的记录，请调大输入年份')

        p_len = len(Config.parameter)  #自动计算参数列表长度
        info = []  #实际待填充的字段，最后用于生成Series的value部分

        for s in range(p_len):
            info.append(-1)  #初始化为-1，代表还未填充

    #    #资产负债表中查询与填充
    #    # 此处需要把 -- 的选项替换成 0
        for i in range(len(result)):
            if result[i] == '--':
                result[i] = '0'

        data1 = result[1:]  #获得资产负债表信息
        info[0] = DataTreat(data1[37])  #总资产
        debt = DataTreat(data1[65])  #总负债
        info[2] = round((debt / info[0]), 2)  #资产负债比
        info[1] = info[0] - debt  #净资产
        info[3] = DataTreat(data1[16])  #流动资产
        info[4] = DataTreat(data1[52])  #一年内到期的长期负债
        info[5] = DataTreat(data1[4])  #应收账款
        info[6] = DataTreat(data1[42])  #预收账款
        info[7] = DataTreat(data1[10])  #存货
        CurrentLiabilities = DataTreat(data1[54])  #流动负载

        #去年的资产负载表
        data1_last = result_last  #获得去年年末资产负债表信息
        # 此处需要把 -- 的选项替换成 0
        for i in range(len(data1_last)):
            if data1_last[i] == '--':
                data1_last[i] = '0'
        AssetLastYear = DataTreat(data1_last[37])  #总资产
        InventoryLastYear = DataTreat(data1_last[10])  #去年存货

        #    #利润表查询与填充
        with open(prefix + stock_id + suffix_profit, 'r') as csvfile:
            csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
            head_parameter = next(csv_reader)  # 读取第一行每一列的标题
            while True:
                try:
                    data = next(csv_reader)  # 读取第一行每一列的标题
                    if data[0] == time_str_last_year:  #获取去年的年报信息
                        result_last = data
                    if data[0] == time_str:  #获取当前的待查询的信息
                        result = data
                        break
                except:
                    print('error')
                    break
        try:
            trash = result_last
        except:
            print('没有前一年的记录，请调大输入年份')
        # 此处需要把 -- 的选项替换成 0
        for i in range(len(result)):
            if result[i] == '--':
                result[i] = '0'
    #    data2 = result #获得资产负债表信息
        data2 = result[1:]  #此处有bug 啊！！！
        ##    print(data)
        info[8] = DataTreat(data2[0])  #营业收入
        info[9] = DataTreat(data2[2])  #营业总成本
        info[10] = DataTreat(data2[4])  #营业税金及附加
        info[11] = DataTreat(data2[7])  #财务费用
        LossFromAssetDevaluation = DataTreat(data2[8])  #资产减值损失
        IncomeFromInvestment = DataTreat(data2[10])  #投资收益
        info[12] = DataTreat(data2[14])  #营业外收入
        NonbusinessExpenditure = DataTreat(data2[15])  #营业外支出
        info[13] = DataTreat(data2[19])  #净利润

        #非经常性盈利损失（此处只计算了前4项，会对计算除非净利润带来不准确）
        NonRecurringProfitAndLoss = info[
            12] - NonbusinessExpenditure + IncomeFromInvestment - LossFromAssetDevaluation
        #除非净利润=净利润-非经常性盈利损失
        info[14] = info[13] - NonRecurringProfitAndLoss  #除非净利润
        info[15] = DataTreat(data2[22])  #每股收益
        if (info[15] <= 0):
            print("无法正确计算股本")
            raise Exception
            return
        stock_num = info[13] / info[15]  #股份数量
        #上一年度利润表
        data2_last = result_last  #获得资产负债表信息
        # 此处需要把 -- 的选项替换成 0
        for i in range(len(data2_last)):
            if data2_last[i] == '--':
                data2_last[i] = '0'

        RevenueLast = DataTreat(data2_last[1])  #营业收入
        NonbusinessIncomeLast = DataTreat(data2_last[14])  #营业外收入
        IncomeFromInvestmentLast = DataTreat(data2_last[10])  #投资收益
        NonbusinessExpenditureLast = DataTreat(data2_last[15])  #营业外支出
        LossFromAssetDevaluationLast = DataTreat(data2_last[8])  #资产减值损失
        NonRecurringProfitAndLossLast = NonbusinessIncomeLast + IncomeFromInvestmentLast - NonbusinessExpenditureLast - LossFromAssetDevaluationLast
        NetProfit = DataTreat(data2_last[19])  #净利润
        NullNetProfit = NetProfit - NonRecurringProfitAndLossLast
        #
        #    #现金流量表查询与填充
        with open(prefix + stock_id + suffix_cash_flow, 'r') as csvfile:
            csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
            head_parameter = next(csv_reader)  # 读取第一行每一列的标题
            #        print(head_parameter)
            while True:
                try:
                    data = next(csv_reader)  # 读取第一行每一列的标题
                    if data[0] == time_str_last_year:  #获取去年的年报信息
                        result_last = data
                    if data[0] == time_str:  #获取当前的待查询的信息
                        result = data
                        break
                except:
                    print('error')
                    break
        try:
            trash = result_last
        except:
            print('没有前一年的记录，请调大输入年份')
    #    # 此处需要把 -- 的选项替换成 0
        for i in range(len(result)):
            if result[i] == '--':
                result[i] = '0'
        data3 = result[1:]  #获得资产负债表信息
        info[16] = DataTreat(data3[9])  #经营净额
        info[17] = DataTreat(data3[21])  #投资净额
        info[18] = DataTreat(data3[33])  #筹资净额
        info[19] = DataTreat(data3[34])  #汇率影响
        #
        #    #现金净增加额=现金的期末余额-现金的期初余额
        info[20] = DataTreat(data3[67]) - DataTreat(data3[66])  #现金净增加额
        info[21] = DataTreat(data3[67])  #期末现金余额
        #
        #
        #    #指标计算，可能还需要获取额外的数据如实时股价等。。。
        #
        #    #流动比率＝流动资产（3）/流动负债（h55）x100%
        info[22] = round(info[3] / CurrentLiabilities, 2)  #流动比率
        #
        #
        #    #资金周转率=本期销售收入净额（营业收入）*2/（资产总额期初余额+资产总额期末余额），期末期初按一年计算
        info[23] = round(info[8] * 2 / (info[0] + AssetLastYear), 2)
        #
        #    #存货周转率 = 营业成本 / 平均存货 ，平均存货=（期初存贷余额+期末存贷余额)/2,按一年期进行计算
        info[24] = round(info[9] * 2 / (info[7] + InventoryLastYear), 2)
        #

        DatStr = datetime(year, 12, 31)
        cnt = 30  #考察连续30个交易日是否有数据
        while cnt > 0:  #获取年尾的数据，排除节假日，停牌的情况.无法排除未上市的情况
            day = DatStr.strftime('%Y%m%d')
            if trade_day.is_tradeday(day):
                cnt -= 1
                cur_price = DataTreat(get_price.get_close_price(stock_id, day))
                if cur_price > 0.1:
                    #                print(day)
                    #                print(cur_price)
                    break
            DatStr -= timedelta(1)
        if cnt <= 0:  #连续60个交易日无数据，说明该公司长期停牌
            cur_price = 0
            print('warning,', year, ',', stock_id, 'has no data')
    #    print (cur_price)
    #    print (date)

        info[25] = round(cur_price * stock_num / info[1], 2)
        info[26] = round(cur_price / info[15], 2)  #静态市盈率
        info[27] = round(info[1] / stock_num, 2)  #市净率

        #    DataTushare =  (ts.get_today_all().values)[0]
        #    per = DataTushare[11]
        #    pb = DataTushare[12]
        #    mktcap = DataTushare[13]
        #    info[25] =  round(mktcap / info[1],2) #总市值/净资
        #    info[26] =  per #市盈率
        #    info[27] = pb #市净率

        #真实净资产收益率 = 净利润 * 2 / (本年期初净资产+本年期末净资产)
        NetAssetEnd = info[0] - debt
        NetAssetBegin = DataTreat(data1_last[37]) - DataTreat(data1_last[65])
        info[29] = round(info[13] * 2 / (NetAssetEnd + NetAssetBegin), 2)
        #名义净资产收益率 = 真实净资产收益率 * 市净率
        info[28] = round(info[29] * info[27], 2)

        #    #毛利率 = （营业收入 - 营业成本） / 营业成本 * 100%
        info[30] = round((info[8] - info[9]) / info[9], 2)

        #    #营收增长率 = (本年度营业收入 - 上年度营业收入) /上年度营业收入 *100%
        info[31] = round((info[8] - RevenueLast) / RevenueLast, 2)
        #
        #    #除非净利润增长率 = (年末 - 年初)/ 年初 * 100%
        info[32] = round((info[14] - NullNetProfit) / NullNetProfit, 2)

        px, Date = get_dividends_history.get_px_single_year(stock_id, year - 1)
        if px == 0.0 or Date == '--':
            info[33] = 0
        elif px == -1:
            info[33] = 0
        else:
            DatStr = datetime.strptime(Date, '%Y%m%d')
            cnt = 30  #考察连续30个交易日是否有数据
            while cnt > 0:  #获取年尾的数据，排除节假日，停牌的情况.无法排除未上市的情况
                day = DatStr.strftime('%Y%m%d')
                #        print(day)
                if trade_day.is_tradeday(day):
                    cnt -= 1
                    cur_price = float(
                        get_price.get_close_price(str(stock_id), day))
                    if cur_price > 0.1:
                        info[33] = round(float(px) / 10 / float(cur_price), 3)
                        break
                DatStr -= timedelta(1)

    #    info[33] = round(float(px) / 10 / float(cur_price),3)
        info[34] = round(float(px) / 10 / info[15], 3)
        #print(pd.Series(info,index = para))
        return pd.Series(info, index=Config.parameter)

    # 以下均为辅助函数，用户不用关心

    def Compare2Themself(self, target_id, start_year=2010):
        '''
        辅助函数：获取target_id从2010年开始直到去年的财务数据，形成DataFrame并输出（用户不必关心）
        输入：开始时间（可选）
        输出：DataFrame形式的结果
        '''
        result = []
        index_id = []
        print('get self report data...')
        for year in range(start_year, datetime.now().year):
            try:
                if self.DataSource == 'SQL':
                    # a = GetItemInfo.GetSingleItem(target_id, year)
                    pass
                elif self.DataSource == 'CSV':
                    a = self.GetSingleLocalItem(target_id, year)
                else:
                    print('compare failure. bad parameter')
                    return
                result.append(a)
                index_id.append(year)
            except Exception as e:
                print('except:', e)
                print('pass ', str(year))
                pass
            # a = self.GetSingleLocalItem(target_id, year)
            # result.append(a)
            # index_id.append(year)
        result = pd.DataFrame(result, index=index_id)
        return result

    def Compare2Industry(self, company):
        '''
        辅助函数：获取配置文件中所指代公司的上一年年报数据，用于同行业对比（用户不必关心）
        输入：行业对比
        输出：DataFrame形式的结果（最后一行是输入的平均水平）
        '''
        result = []
        index_id = []
        print('get compare report data...')
        for individual in company:
            try:
                if self.DataSource == 'SQL':
                    # a = GetItemInfo.GetSingleItem(individual,
                    #                               datetime.now().year - 1)
                    pass
                elif self.DataSource == 'CSV':
                    a = self.GetSingleLocalItem(individual,
                                                datetime.now().year - 1)
                else:
                    print('compare failure. bad parameter')
                    return
                result.append(a)
                index_id.append(individual)
            except Exception as e:
                if self.DataSource == 'SQL':
                    # a = GetItemInfo.GetSingleItem(individual,
                    #                               datetime.now().year - 1)
                    pass
                elif self.DataSource == 'CSV':
                    a = self.GetSingleLocalItem(individual,
                                            datetime.now().year - 2)
                else:
                    print('compare failure. bad parameter')
                    return
                result.append(a)
                index_id.append(individual)
        result = pd.DataFrame(result, index=index_id)
        result.loc['avarage'] = result.apply(lambda x: x.sum() / len(index_id))
        #    result.to_csv('compare_industry.csv')
        return result


if __name__ == '__main__':
    id_list = ['000651', '000333']
    BasePath = '.\\easydo\\Algorithm\\M1809'
    HstPath = os.path.join(BasePath, "history_data")  # 历史数据路径
    getDataObj = GetData("CSV")
    # data1 = getDataObj.GetSingleLocalItem('000651', 2017)
    # print(data1)
    # # data2 = getDataObj.Compare2Themself('000333')
    # # print (data2)
    data3 = getDataObj.Compare2Industry(id_list)
    print(data3)
