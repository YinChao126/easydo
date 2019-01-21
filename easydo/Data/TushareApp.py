# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 11:01:27 2018

@author: yinchao
"""
import pandas as pd
import tushare as ts
from datetime import datetime
from datetime import timedelta
import time

import os,sys
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import Miscellaneous.TimeConverter as TimeConverter

class ts_app:
    '''
    类名：ts_pro
    功能：利用tushare_pro数据接口实现的相关应用功能
    更新时间：2010-1-1
    应用函数一览表：
    BasicInfo:获得指定个股最新的基础情况（收盘价、PE、换手率、股本数等）（非常重要）
    GetPrice:获得指定个股指定一天的收盘价，如果当天没有则自动往前找
    GetOneYearFinanceTable:获得指定个股指定一年的财务统计数据
    GetFinanceTable:获得指定个股连续n年的年度财务统计数据（非常重要）
    GetDividendTable:获得指定个股的全部分红历史（非常重要）
    
    AvgExchangeInfo:平均交易参数（换手率、PE_TTM、PB） （非常重要）
    AvgBasicInfo:平均财务指标（roe, 资产负债率）（非常重要）
    AvgGrowthInfo:增长指标（营收增长率、净利润增长率）（非常重要）
    update：一次性更新avg_info.csv文件
    
    备注：
    1. 财务统计表的item可以通过修改fields属性(详情请看最后面的附录或官网解释)
    '''
    def __init__(self):
        '''
        此处的token请勿修改
        fields建议不要改动，自定义的字段请在append_table中添加
        '''
        token_file = os.path.dirname(BASE_DIR)+r'\parameter.cfg'
        with open(token_file, 'r') as fh:
            content = fh.read()
        try:
            ts.set_token(content)
            self.pro = ts.pro_api(content)
            self.fields = ['ts_code','end_date','roe_yearly','eps','dt_eps','bps','cfps',
                       'debt_to_assets','ebit_of_gr','roe_waa','roa']
            append_table = ['basic_eps_yoy','dt_eps_yoy','op_yoy'] #自主添加
            self.fields += append_table
        
            self.save_path = 'avg_info.csv'
        except:
            print('tushare初始化失败，请确保parameter.cfg放在根目录下')
    def GetPrice(self, ID,cur_day = 0):
        '''
        获取指定一天的收盘价，默认获取最近一天的价格
        @输入： ID(str)-> '600660.SH'
               cur_day(str/datetime) -> '20181012', '2018-10-12', datetime类型 
        @返回值：price(float)价格  day(datetime)实际日期
        备注：如果连续60天都找不到，则返回0（长时间停牌或者未上市）
        '''
        cnt = 60
        if cur_day == 0:
            cur_day = datetime.now()  
        else:
            cur_day = TimeConverter.str2dtime(cur_day)
        if cur_day.year < 1991:
            return 0
        while True:
            day = TimeConverter.dtime2str(cur_day)
            data = self.pro.daily_basic(ts_code=ID, trade_date=day, fields='trade_date,close')       
            if data.empty != True:
                break
            cur_day -= timedelta(1) 
            cnt -= 1
            if cnt < 0:
                return 0
        price = data.iloc[0]['close']
#        print(ID, day, price)
        return price, day
    
    def GetFinanceTable(self, ID, n):
        '''
        获得指定个股连续n年的财务统计数据
        @输入： ID(str)->'600660.SH'   n(int)->最近n年的数据
        @返回值：DataFrame格式的单年度财务报表
        '''
        day_list = []
        laster_year = str(datetime.now().year - 1)
        data = self.pro.query('fina_indicator', ts_code=ID, fields=self.fields,period=laster_year)
        if data.empty == True: #如果去年的年报还没出来，则n+1
            n += 1
            
        for s in range(datetime.now().year - 1 - n,datetime.now().year - 1):
            day = str(s)+'1231'
            day_list.append(day)
            
        data = pd.DataFrame(columns=self.fields)
        stop = datetime.now().year - 1
        if n < 5:
            start = stop - n + 1
            str_start = str(start) + '0101'
            str_stop = str(stop) + '1231'
    #        print(str_start, str_stop)
            tmp = self.pro.query('fina_indicator', ts_code=ID, fields=self.fields, start_date=str_start, end_date=str_stop)
            data = pd.concat([data, tmp], axis = 0)
            
        else:
            while (n - 5) >= 0: #一次性最多获取5年数据
                start = stop - 5 + 1
                str_start = str(start) + '0101'
                str_stop = str(stop) + '1231'
    #            print(str_start, str_stop)
                tmp = self.pro.query('fina_indicator', ts_code=ID, fields=self.fields, start_date=str_start, end_date=str_stop)
                data = pd.concat([data, tmp], axis = 0)
                n -= 5
                stop -= 5
            if n > 0:
                start -= n
    #            print(n, start, stop)
                
                str_start = str(start) + '0101'
                str_stop = str(stop) + '1231'
    #            print(str_start, str_stop)
                tmp = self.pro.query('fina_indicator', ts_code=ID, fields=self.fields, start_date=str_start, end_date=str_stop)
                data = pd.concat([data, tmp], axis = 0)
                    
        '''
        此处，data最多返回60条记录
        需要将data分成多段
        '''
        new = pd.DataFrame(columns=self.fields)    
        for item in day_list:
            df_result = data[data.end_date == item]
            if df_result.empty == False:
                new = pd.concat([new, df_result], axis = 0)
        
        new.drop_duplicates(subset=['end_date'],keep='first',inplace=True)
        new.index = range(len(new))
        new = new.reindex(columns=self.fields)
        return new
    
    def GetOneYearFinanceTable(self, ID, year):
        '''
        获得指定个股某一年的财务统计数据
        @输入： ID(str)->'600660.SH'   year(str/int)->2017
        @返回值：DataFrame格式的单年度财务报表
        '''
        try:
            day = str(year)+'1231'
        except:
            day = year + '1231'
        data = self.pro.query('fina_indicator', ts_code=ID, period=day,fields=self.fields)
        data = data.reindex(columns=self.fields)
        data.drop_duplicates(subset=['end_date'],keep='first',inplace=True)
        return data
    
    def GetDividendTable(self, ID):
        '''
        获得指定个股的分红记录
        备注：数据来源于tushare的接口
        分红、送股都是按每股送多少而定
        '''
        pro = ts.pro_api()
#        df = pro.dividend(ts_code = ID)
        dividend_fields = 'ts_code,end_date,div_proc,stk_bo_rate,stk_co_rate,cash_div_tax,ex_date'
        df = pro.dividend(ts_code=ID, fields=dividend_fields)
#        print(df)
        length = len(df)
        ts_code = df['ts_code']
        end_date = df['end_date']
        years = []
        for s in end_date:
            result = s[:4]
            years.append(result)
        cash_div_tax = df['cash_div_tax']
        stk_co_rate = df['stk_co_rate'].copy()
        for i in range(length):
            if stk_co_rate[i] != stk_co_rate[i]:
                stk_co_rate[i] = 0
        stk_bo_rate = df['stk_bo_rate'].copy()
        for i in range(length):
            if stk_bo_rate[i] != stk_bo_rate[i]:
                stk_bo_rate[i] = 0
        ex_date = df['ex_date']
        out = pd.DataFrame(list(zip(ts_code,years,cash_div_tax,stk_co_rate,stk_bo_rate,ex_date)),columns=['名称','年度','派息','转股','送股','除权日'])
        for i in range(length):
            if ex_date[i] == None:
                out = out.drop(i)
        out = out.sort_values(by=['年度'])
        out.index = range(len(out))
        return out
    def BasicInfo(self, ID):
        '''
        输入一个个股和开始日期，获得一个DataFrame格式基本情况列表
        @输入：
        ID(str) 
        start_day(str) 开始时间： '20100101'
        @返回：DataFrame格式数据的基础信息
        
        备注：该函数为辅助函数，用户禁止调用
        '''
        stop_day = datetime.now()
        cnt = 200
        while cnt > 0: #获得第一天
            day = TimeConverter.dtime2str(stop_day)
            data = self.pro.daily_basic(ts_code=ID, trade_date=day, fields='trade_date, ts_code, close, turnover_rate,pe, pe_ttm,pb,total_share')
            stop_day -= timedelta(1)
            cnt -= 1
            if data.empty != True:
                return data
        return 0
        
    def _DailyRecord(self, ID, start_day):
        '''
        输入一个个股和开始日期，获得一个DataFrame格式基本情况列表
        @输入：
        ID(str) 
        start_day(str) 开始时间： '20100101'
        @返回：DataFrame格式数据的基础信息
        
        备注：该函数为辅助函数，用户禁止调用
        '''
        stop_day = datetime.now()
        cur_day = TimeConverter.str2dtime(start_day)
        data = pd.DataFrame(columns=['trade_date','turnover_rate','pe_ttm','pb'])
        while cur_day < stop_day:
            if cur_day.weekday() < 5:
                try:
                    day = TimeConverter.dtime2str(cur_day)
                    info = self.pro.daily_basic(ts_code=ID, trade_date=day, fields='trade_date,turnover_rate,pe_ttm,pb')
                    data = pd.concat([data, info], axis = 0)
                    time.sleep(0.2)
                    print(day)
                except:
                    pass
            cur_day += timedelta(1)
        data.index = range(len(data))
        return data
    
    def AvgExchangeInfo(self, ID, years):
        '''
        输入一个个股，获得其基本的参数，平均换手率，平均静态市盈率，平均pb值
        备注：数据来源于avg_info.csv
        @输入：
        @ID(str)->个股ID号    years(int)->平均几年的水平
        输出：平均换手率、平均PE_TTM、平均PB(均为float类型)
        '''
        self.update_one(ID, years)
        content = pd.read_csv(self.save_path)
        try:
            item = content[(content.id == ID) & (content.year == years)]
            turnover = item.iloc[-1]['turnover']
            pe = item.iloc[-1]['pe']
            pb = item.iloc[-1]['pb']
            return turnover, pe, pb
        except:
            return 0, 0, 0
        
    def AvgGrowthInfo(self, ID, years = 5):
        '''
        @描述： 输入一个个股，求得其连续n年的平均增长率水平
        @输入： ID(str)-> '600660.SH' years(int)->多少年的平均值
        @返回： growth(float)->平均n年稀释每股收益同比增长率
        @备注： 该平均水平是加权求平均，越近的权值越大
        '''
        data = self.GetFinanceTable(ID, years)
        g_eps = data['dt_eps_yoy'].mean() #g_eps每股收益增长率
        g_eps = round(g_eps/100, 4)
        if g_eps != g_eps: #如果g_eps == nan则算基础eps增长率
            g_eps = data['basic_eps_yoy'].mean() #g_eps每股收益增长率
            g_eps = round(g_eps/100, 4)
        g_op = data['op_yoy'].mean() #g_op营业利润增长率
        return g_eps
        
    def _GetAvgInfo(self, ID,start_day):
        '''
        输入一个个股，获得其基本的参数，平均换手率，平均静态市盈率，平均pb值
        备注：数据来源于tushare
        为了客观，PE、PB的求值剔除了10%最高价和10%最低价
        @输入：
        @ID(str) 
        @start_day(str) 开始时间： '20100101'
        输出：平均换手率、平均PE_TTM、平均PB
        '''
        stop_day = datetime.now() - timedelta(1)
        cur_day = TimeConverter.str2dtime(start_day)
        while cur_day < stop_day: #获得第一天
            day = TimeConverter.dtime2str(cur_day)
            data = self.pro.daily_basic(ts_code=ID, trade_date=day, fields='trade_date,turnover_rate,pe_ttm,pb')
            cur_day += timedelta(1)        
            if data.empty != True:
                break
        if data.empty == True:
            print('no data')
            return 0
        
        while cur_day < stop_day:
            if cur_day.weekday() < 5:
                try:
                    day = TimeConverter.dtime2str(cur_day)
                    info = self.pro.daily_basic(ts_code=ID, trade_date=day, fields='trade_date,turnover_rate,pe_ttm,pb')
                    data = pd.concat([data, info], axis = 0)
                    time.sleep(0.2)
                    print(cur_day)
                except:
                    pass
            cur_day += timedelta(1)
        
        data_copy = data.copy()
        
        #绘图
    #    plt.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签
    #    plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
    #    plt.figure()
    #    
    #    换手率 = data_copy['turnover_rate']
    #    平均市盈率 = data_copy['pe_ttm']
    #    平均市净率 = data_copy['pb']
    #    p1=换手率.plot(label=u'原始数据图')
    #    plt.grid(True)
    #    plt.show()
    #    return data_copy['pe_ttm']
        
    
        #分析
        data_copy = data_copy.sort_values(by='pe_ttm')
        total_len = len(data)
        per_id = int(total_len * 0.1)
        suf_id = int(total_len * 0.9)
        data_left = data_copy[per_id:suf_id] #筛除牛市和熊市的影响
        print(len(data_copy), len(data_left))
        
        pe_ttm = data_left['pe_ttm'] #获取PE的平均水平
        turnover = data_left['turnover_rate']
        pb = data_left['pb']
        avg_pe = round(pe_ttm.mean(),2)
        avg_turnover = round(turnover.mean(),2)
        avg_pb = round(pb.mean(),2)
        return avg_turnover, avg_pe, avg_pb
    
    def update(self):
        '''
        更新agv_info.csv到最近一天
        '''
        today = datetime.now()
        if today.hour < 15: #如果当天还未收盘，则更新到昨天
            today -= timedelta(1)
        content = pd.read_csv(self.save_path)
        for i in range(len(content)):
            item = content.loc[i]
            stop_day = item['stop_day']
            if TimeConverter.is_equal(today, stop_day) == True:
                continue
            id_str = item['id']
            years = item['year']
            self.update_one(id_str, years)
            
    def update_one(self, id_str, years):
        '''
        辅助函数，用户禁止调用
        描述：更新单条记录到最近一天
        csv文件定义：
        文件名：avg_info.csv
        字段： id, year, days, stop_day, turnover, pe, pb
        '''
        if len(id_str) != 9 or isinstance(id_str, str) == False or years < 1:
            print('输入非法')
            return
        file_name = self.save_path
        header = ['id','year','days','stop_day','turnover','pe','pb']
        try:
            records = pd.read_csv(file_name)
        except:
            header = ['id','year','days','stop_day','turnover','pe','pb']
            records = pd.DataFrame(columns=header)
        
        df_result = records[(records.id == id_str) & (records.year == years)]
#        print(df_result)
#        return
        if df_result.empty == True:
            print('没有这条记录，重新更新')
            today = datetime.now()
            default_data = {'id':id_str,
                            'year':years,
                            'days':0,
                            'stop_day':TimeConverter.dtime2str(today,'/'),
                            'turnover':0.0,
                            'pe':0.0,
                            'pb':0.0}
            index_name = len(records)
            item = pd.DataFrame(default_data,index=[index_name])
#            print(item)
            
            update_day = today - timedelta(years * 365)
#            update_day = today - timedelta(10)
#            print(update_day, today)
            append_list = self._DailyRecord(id_str,TimeConverter.dtime2str(update_day))
#            print(append_list)
            new_turnover = round(append_list['turnover_rate'].mean(),2)
            new_pe = round(append_list['pe_ttm'].mean(),2)
            new_pb = round(append_list['pb'].mean(),2)
            total_day = len(append_list) #新增多少天？update_item.loc[index_name,'turnover']=new_turnover
            item.loc[index_name,'days']=total_day
            item.loc[index_name,'turnover'] = new_turnover
            item.loc[index_name,'pe']=new_pe
            item.loc[index_name,'pb'] = new_pb
#            print(new_turnover,new_pe,new_pb,total_day)
#            print('更新前')
#            print(records)
            records = pd.concat([records,item])
#            records = records.sort_index()
            records = records.sort_values(by=['id','year'])
#            print('更新后')
#            print(records)
            records.to_csv(file_name,index =False)
        else:
            print('已有记录，直接在原有基础上更新即可')
            '''
            此处有bug
            loc[0,'xxx']已经变了，首次是0，之后都是1了。。
            '''
            index_name = df_result.index.tolist()[0]
            old_turnover = df_result.loc[index_name,'turnover'] #此处的bug在于0不是第一行！！
            old_pe = df_result.loc[index_name,'pe']
            old_pb = df_result.loc[index_name,'pb']
            total_day = df_result.loc[index_name,'days']            
            start_day = df_result.loc[index_name,'stop_day']
            start_day = TimeConverter.str2dtime(start_day)
            today = datetime.now()
#            print(start_day, today)
            if TimeConverter.dtime2str(start_day) == TimeConverter.dtime2str(today):
                print('already latest')
                return 0
            
#            print(start_day)
#            print('old value:',old_turnover, old_pe, old_pb)
            append_list = self._DailyRecord(id_str,TimeConverter.dtime2str(start_day))
            if isinstance(append_list,int): #最近更新的那一天没有记录（周末或者节假日）
                print('already latest')
                return
            turnover_add = append_list['turnover_rate'].sum()
            pe_add = append_list['pe_ttm'].sum()
            pb_add = append_list['pb'].sum()
            add_day = len(append_list) #新增多少天？
#            print(add_day, turnover_add, pe_add, pb_add)
            new_turnover = round(((total_day - add_day) * old_turnover + turnover_add) / total_day, 2)
            new_pe = round(((total_day - add_day) * old_pe + pe_add) / total_day, 2)
            new_pb = round(((total_day - add_day) * old_pb + pb_add) / total_day, 2)
#            print(new_turnover, new_pe, new_pb)
            #获得更新列
        
            update_item = df_result.copy()
#            index_name = df_result.index.tolist()[0]
#            print(update_item)
            update_item.loc[index_name,'stop_day']=TimeConverter.dtime2str(today,'/')
            update_item.loc[index_name,'turnover']=new_turnover
            update_item.loc[index_name,'pe']=new_pe
            update_item.loc[index_name,'pb'] = new_pb
#            print(update_item)
            
        
            #更新原有的records
#            print('更新前')
#            print(records)
            drop_item = records[(records.id == id_str) & (records.year == years)]
            drop_index = drop_item.index.tolist()[0]
            records = records.drop([drop_index])
            records = pd.concat([records,update_item])
#            records = records.sort_index()
            records = records.sort_values(by=['id','year'])
#            print('更新后')
#            print(records)
            records.to_csv(file_name,index =False)
        
#b = pro.fina_indicator(ts_code='600660.SH') #获取所有财务指标
#print(b)



    
def get_rate(data):
    '''
    输入一个Series，获取其增长率
    '''
    r = []
    last = 0
    
    
    if isinstance(data, pd.core.series.Series): #数据类型转换
        data = data.tolist()
        d1 = []
        for i in data:
            d1.append(float(i))
            data = d1
    
    for s in data:
        if last > 0:
            rate = round((s - last) / last * 100,2) 
            r.append(rate)
        else:
            r.append(0.0)
        last = s
    return r
def get_increase(dataframe, column):
    '''
    输入一个dataframe数据，指定其column名称，获取其float类型的增长率
    '''
    data = dataframe[column].tolist()
    d1 = []
    for i in data:
        d1.append(float(i))
        data = d1
    return data
    
    
def get_point(data):
    '''
    描述：获取一个增长序列的风险和年化收益率
    输入：data必须是一个年收益率的series
    输出：a->序列的方差（风险）， b->序列的增长率 
    备注：可以改造成一个月线增长率的函数，但是标准差就要乘以根号12，年化收益率就要乘以12
    '''
    if isinstance(data,list): #数据类型转换
        data = pd.Series(data)
    a = data.std()
    b = 1
    for s in data:
        b = b * (1 + s)
    return round(a,4), round((b-1)/len(data), 4)

#def GetGrowthList(ID,count = 0):
#    '''
#    输入个股，求得其连续n年的eps列表，然后得到年度增长记录
#    输出：(年均增长率,增长方差）
#    '''
#    raw_data = GetYearFinanceTable(ID)
#    if raw_data.empty == True:
#        return 0
##    print(raw_data)
#    a = raw_data.columns.values.tolist()
#    
#    print(a)
#    eps = raw_data['equity_yoy']
#    print(eps)


'''
附录：
fields定义如下(已删除明显没用的字段，完全定义请看链接)：
https://tushare.pro/document/2?doc_id=79

#基础参数
ts_code	str	TS代码
end_date	str	报告期

#至关重要的参数
dt_eps	float	稀释每股收益
bps	float	每股净资产
cfps	float	每股现金流量净额
debt_to_assets	float	资产负债率
ebit_of_gr	float	息税前利润/营业总收入（毛利率）
roe	float	净资产收益率
roe_waa	float	加权平均净资产收益率
roa	float	总资产报酬率

#已有统计直接拿来用（也可以自己算出来）
op_yoy	float	营业利润同比增长率(%)
or_yoy	float	营业收入同比增长率(%)
dt_eps_yoy	float	稀释每股收益同比增长率(%)
bps_yoy	float	每股净资产相对年初增长率(%)
assets_yoy	float	资产总计相对年初增长率(%)
roe_yoy	float	净资产收益率(摊薄)同比增长率(%)

#################以下均为具体分析用######################
#资产结构分析
ebit_to_interest	float	已获利息倍数(EBIT/利息费用)
debt_to_assets	float	资产负债率
capitalized_to_da	float	资本支出/折旧和摊销
ca_to_assets	float	流动资产/总资产
nca_to_assets	float	非流动资产/总资产
tbassets_to_totalassets	float	有形资产/总资产
int_to_talcap	float	带息债务/全部投入资本
eqt_to_talcapital	float	归属于母公司的股东权益/全部投入资本
currentdebt_to_debt	float	流动负债/负债合计
longdeb_to_debt	float	非流动负债/负债合计
ocf_to_shortdebt	float	经营活动产生的现金流量净额/流动负债
debt_to_eqt	float	产权比率
eqt_to_debt	float	归属于母公司的股东权益/负债合计
eqt_to_interestdebt	float	归属于母公司的股东权益/带息债务
tangibleasset_to_debt	float	有形资产/负债合计
tangasset_to_intdebt	float	有形资产/带息债务
tangibleasset_to_netdebt	float	有形资产/净债务
fixed_assets	float	固定资产合计


#营运分析
current_ratio	float	流动比率
quick_ratio	float	速动比率
inv_turn	float	存货周转率
ar_turn	float	应收账款周转率
assets_turn	float	总资产周转率

#盈利分析
profit_to_op	float	利润总额／营业收入
op_of_gr	float	营业利润/营业总收入
profit_to_gr	float	净利润/营业总收入
finaexp_of_gr	float	财务费用/营业总收入
equity_yoy	float	净资产同比增长率
opincome_of_ebt	float	经营活动净收益/利润总额
investincome_of_ebt	float	价值变动净收益/利润总额
n_op_profit_of_ebt	float	营业外收支净额/利润总额
dtprofit_to_profit	float	扣除非经常损益后的净利润/净利润

#现金流分析
salescash_to_or	float	销售商品提供劳务收到的现金/营业收入
ocf_to_or	float	经营活动产生的现金流量净额/营业收入
ocf_to_opincome	float	经营活动产生的现金流量净额/经营活动净收益

#其他
eps	float	基本每股收益
roic	float	投入资本回报率
assets_to_eqt	float	权益乘数
longdebt_to_workingcapital	float	长期债务与营运资金比率
#######################################################
2   240  601012.SH  3.92  17.05  2019/01/03      1.03     1
3   488  601012.SH  3.96  20.04  2019/01/03      1.11     2
4   731  601012.SH  3.86  24.61  2019/01/03      1.18     3
5   946  601012.SH  4.34  37.39  2019/01/03      2.27     4
6  1189  601012.SH  4.04  39.52  2019/01/03      2.28     5
'''







if __name__ == '__main__':
    l = '600660.SH'
    id_str = '000651.SZ'
    app = ts_app()
#    app.update()
#    a = app.AvgExchangeInfo(l, '20181111')
#    print(a)
    
    b = app.GetPrice(l,'20180101')
    print(b)
#    app.update_one(l,2)
#    for s in range(1,6):
#        app.update_one(id_str,s)
    
#    a = app._DailyRecord(l,'20181220')
#    print(a)
#    c = app.GetFinanceTable('600660.SH',12)
##    c = app.GetOneYearFinanceTable('600377.SH', 2017)
#    print(c)

