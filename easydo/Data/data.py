import get_price
import pandas as pd
import tushare as ts

class data:
    def __init__(self):
        self.data = 0
    
    def get_yesterday_price(self, stock_id):
        return get_price.get_close_price(stock_id)

    def get_price(self, stock_id, date = 0):
        return get_price.get_close_price(stock_id, date)
    '''
    获取一段时间内的k线
    '''   
    def get_period_k_day(self, id, start_day, stop_day = 0):
        return get_price.get_period_k_day(id, start_day, stop_day)

    '''
    获取一段时间内的指数
    ''' 
    def get_index_data(self,id):
        api = ts.pro_api('2dbe42e7773b4591a74a07d19a30f3f7d9a663f2023f27f6e38dfde1')
        a = []
        for i in range(1990,2030,5):
            print(i)
            print(str(i)+'0101')
            print(str(i+5)+'0101')
            a.append(ts.pro_bar(pro_api=api, ts_code=id, asset='I', start_date=str(i)+'0101', end_date=str(i+5)+'0101'))
        return pd.concat(a).drop_duplicates()   

    '''
    股票列表,包括属性：
    code,代码
    name,名称
    industry,所属行业
    area,地区
    pe,市盈率
    outstanding,流通股本(亿)
    totals,总股本(亿)
    totalAssets,总资产(万)
    liquidAssets,流动资产
    fixedAssets,固定资产
    reserved,公积金
    reservedPerShare,每股公积金
    esp,每股收益
    bvps,每股净资
    pb,市净率
    timeToMarket,上市日期
    undp,未分利润
    perundp, 每股未分配
    rev,收入同比(%)
    profit,利润同比(%)
    gpr,毛利率(%)   
    npr,净利润率(%) 
    holders,股东人数
    '''
    def get_stock_basics(self):
        return ts.get_stock_basics()

    '''
    业绩报告,分为季度,字段如下：
    code,代码
    name,名称
    esp,每股收益
    eps_yoy,每股收益同比(%)
    bvps,每股净资产
    roe,净资产收益率(%)
    epcf,每股现金流量(元)
    net_profits,净利润(万元)
    profits_yoy,净利润同比(%)
    distrib,分配方案
    report_date,发布日期
    '''
    def get_report_data(self,year,quarter):
        return ts.get_report_data(year,quarter)

    '''
    盈利能力,分为季度,字段如下：
    code,代码
    name,名称
    roe,净资产收益率(%)
    net_profit_ratio,净利率(%)
    gross_profit_rate,毛利率(%)
    net_profits,净利润(万元)
    esp,每股收益
    business_income,营业收入(百万元)
    bips,每股主营业务收入(元)
    '''
    def get_profit_data(self,year,quarter):
        return ts.get_profit_data(year,quarter)

    '''
    营运能力,分为季度,字段如下：
    code,代码
    name,名称
    arturnover,应收账款周转率(次)
    arturndays,应收账款周转天数(天)
    inventory_turnover,存货周转率(次)
    inventory_days,存货周转天数(天)
    currentasset_turnover,流动资产周转率(次)
    currentasset_days,流动资产周转天数(天)
    '''
    def get_operation_data(self,year,quarter):
        return ts.get_operation_data(year,quarter)


    '''
    成长能力,分为季度,字段如下：
    code,代码
    name,名称
    mbrg,主营业务收入增长率(%)
    nprg,净利润增长率(%)
    nav,净资产增长率
    targ,总资产增长率
    epsg,每股收益增长率
    seg,股东权益增长率
    '''
    def get_growth_data(self,year,quarter):
        return ts.get_growth_data(year,quarter)


    '''
    偿债能力,分为季度,字段如下：
    code,代码
    name,名称
    currentratio,流动比率
    quickratio,速动比率
    cashratio,现金比率
    icratio,利息支付倍数
    sheqratio,股东权益比率
    adratio,股东权益增长率
    '''
    def get_debtpaying_data(self,year,quarter):
        return ts.get_debtpaying_data(year,quarter)


    '''
    现金流量数据,分为季度,字段如下：
    code,代码
    name,名称
    cf_sales,经营现金净流量对销售收入比率
    rateofreturn,资产的经营现金流量回报率
    cf_nm,经营现金净流量与净利润的比率
    cf_liabilities,经营现金净流量对负债比率
    cashflowratio,现金流量比率
    '''
    def get_cashflow_data(self,year,quarter):
        return ts.get_cashflow_data(year,quarter)            


if __name__ == '__main__':
    import sys
    import os
    BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = BASE_DIR + r'\Data'
    sys.path.append(DATA_DIR)
    
    data = data()
    print(data.get_index_data("000001.SH"))

'''
   print("盈利能力")
    print(data.get_profit_data(2018,2))
    print("营运")
    print(data.get_operation_data(2018,2))
    print("成长")
    print(data.get_growth_data(2018,2))
    print("偿债")
    print(data.get_debtpaying_data(2018,2))
    print("现金流")
    print(data.get_cashflow_data(2018,2))
'''





