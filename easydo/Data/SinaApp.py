# -*- coding: utf-8 -*-
"""
Created on Sat Dec 22 09:05:14 2018

@author: Administrator
#json常识： dumps将字符串转成json， loads将json转成字典， 最后字典可以使用
"""
import requests
import json
import pandas as pd
from datetime import datetime
from datetime import timedelta

import os,sys
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import Miscellaneous.TimeConverter as TimeConverter
class SinaApp:
    '''
    @类名：SinaApp
    @描述：从新浪财经获取的数据
    @已提供API列表：
    >>UpdateKday:更新指定个股的k线数据，如果没有则自动创建，结果持久化到本地或者数据库
    >>GetInfo:获取指定个股某一天的交易数据(close,high,low,open,volume)   
    >>get_k_day:获取指定个股指定天数的K线数据，以DataFrame格式返回
    >>ClosePrice：获取指定个股某一天的收盘价
    '''
    
    def __init__(self):
        '''
        @用户配置：
        data_path:csv文件保存的默认地址
        compatible:兼容模式，开启后使用更方便（效率显著降低）
        兼容模式下：自动检查更新，自动检查输入数据类型并自动切换
        '''
        self.data_path = BASE_DIR + '\\Data\\raw_data\\' #默认文件保存地址
        if os.path.exists(self.data_path) == False:
            os.makedirs(self.data_path)
        self.compatible = True #默认打开，方便使用,想要禁止，请设置为False
        self.log = True #调试语句和显示语句使能开关

    def UpdateKday(self, mid, mode = 'CSV'):
        '''
        @用户接口API：
        @描述：输入一个id列表或者单个id，自动获取其所有的k线历史并自动存档
        @
        '''
        if isinstance(mid, str):
            self.update_one(mid,mode)
        elif isinstance(mid, list):
            for item in mid:
                self.update_one(item,mode)
                
    def update_one(self, id_str,mode = 'CSV'):
        '''
        @描述：检查指定路径下是否包含最新的资源，如果不包含，则更新
        1. 检查是否有该文件
        2. 检查是否为最新记录，不是则更新
        3. 根据mode指定是保存到本地CSV还是到数据库
        @输入：id_str(str)->更新标的，必须是单个股票，且格式固定为： 'sh600660'
              mode->更新方式， CSV:存本地， SQL:存数据库
        @输出：./Data/raw_data/文件夹下自动建立id_str.csv文件
        '''
        if self.log == True:
            print('checking ...')
        file_name = self.data_path + id_str + '.csv'

        try:
            content = pd.read_csv(file_name)  
            latest_record = content.iloc[-1]
            get_today_data = self.get_k_day(id_str,1) #获取最新网络数据
            today_str = get_today_data.iloc[-1]['day'] #今天
            today = TimeConverter.str2dtime(today_str)
            record_str = latest_record['day']  #最新记录的日期
            latest = TimeConverter.str2dtime(record_str)
            
            
            if latest == today: #已经是最新的
                if self.log == True:
                    print('%s already the latest' % id_str)
            else: #append方式更新
                if self.log == True:
                    print('update %s,please wait...' % id_str)
                update_day = abs(today-latest)
                update_day = update_day.days #更新时间
                
                b = self.get_k_day(id_str, update_day)
                for i in range(len(b)):
                    day = b.iloc[i]['day']
                    day = TimeConverter.str2dtime(day)
                    if day > latest:
                        index = i
                        break
                append_item = b[b.index >= index] #最终要更新的内容
                append_item.to_csv(file_name,mode='a', header=False, index = False) 
        except:
            print('no record yet, creating %s.csv,please wait...' % id_str)
            a = self.get_k_day(id_str)
            a.to_csv(file_name,index = False) 
            
        if self.log == True:
            print('finished')   

    def GetInfo(self, id_str, date):
        '''
        @描述：读取csv文件并获取某一天的参数（价格/成交量等）
        @输入：id_str(str)->想要查找的id， 格式如下：'sh600660'
            date(str): 非兼容模式下必须为str类型且为'xxxx-xx-xx'格式，兼容模式下随意
            item(str)：获取什么信息，默认获取收盘价
            item(str) = close/open/high/low/volume
        @输出：
            对应的查询信息，类型为float或者int
        '''
        if self.compatible == True:
            if isinstance(date, datetime):
                date = TimeConverter.dtime2str(date,'-')
            elif isinstance(date, str):
                date = TimeConverter.str2dtime(date)
                date = TimeConverter.dtime2str(date,'-')
            self.UpdateKday(id_str) #自动更新
            
        file_name = self.data_path + id_str + '.csv'
        content = pd.read_csv(file_name)
        result = content[content.day == date]
        return result    
    
    def ClosePrice(self, id_str, date):
        '''
        @描述：获取指定一天的收盘价
        @输入：id_str(str)->‘sh600660’
                date(datetime, str)都可以
        @输出：price(float),  返回0代表没有数据
        '''
        info = self.GetInfo(id_str, date)
        try:
            price = info.iloc[-1]['close']
        except:
            price = 0
        return price
    
    def get_k_day(self, id_str,day=9999):
        '''
        @描述：获取指定ID的K线数据，并以DateFrame形式返回（此为辅助函数，用户禁止直接调用）
        @输入：   id_str-> str类型的id，尤其注意，必须带sh/sz前缀，如："sh600660"
                day->返回的天数，默认是最大值，返回全部历史记录
        @输出： DateFrame形式的K线数据，全部为str类型
                    close         day    high     low    open    volume
                0  22.090  2018-12-14  22.290  21.900  22.090   7427246
                1  22.190  2018-12-17  22.310  21.810  22.050   5286448
        '''
        import re
        prefix = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol='
        tail = '&scale=240&ma=no&datalen='
        if isinstance(day,int):
            day = str(day)
        url = prefix + id_str + tail + day
        response = requests.get(url)
        if response.status_code == 200:
            html = response.content
            html_str = html.decode()
            pattern = r'(?<=[{,])(\w+)' #可以找到
            content = re.sub(pattern, lambda i: '\"'+i.group(1)+'\"', html_str)
            result = json.loads(content)
            
            detail_column = ['close', 'day', 'high', 'low', 'open', 'volume']
            data = pd.DataFrame(columns=detail_column)
            for item in result:
                data = data.append(item, ignore_index=True)
            
            return data
        else:
            return 0    
        
    def add_black_price(self, id_str,day_formate = '%Y-%m-%d'):
        '''
        @描述：给定一个k线csv文件，填充空白的时间，便于快速查找价格
        @备注：此为辅助函数，用户禁止调用
        @输入：     file_name->文件全名
                  day_formate->时间格式转换的参数，默认为'xx-xx-xx',可以改为'xx/xx/xx'
        @输出：out.csv文件， DataFrame格式的变量以备查验
        '''
        file_name = self.data_path + id_str + '.csv'
        content = pd.read_csv(file_name)
        if self.log == True:
            print(content)
    
        ilen = len(content)
        i = 0
        today = datetime.strptime(content.iloc[0]['day'],day_formate)
        yesterday = today
        for i in range(ilen):
            today = datetime.strptime(content.iloc[i]['day'],day_formate)
            a = today.strftime(day_formate)
            d_index = list(content.columns).index('day')
            content.iloc[i,d_index] = a
            
        for i in range(1, ilen):
            today = content.iloc[i]['day']
            today = datetime.strptime(today,day_formate)
            
            if yesterday + timedelta(1) != today:
                cur_day = yesterday + timedelta(1)
                while cur_day < today:
                    s = content.iloc[i-1].copy()
                    s['day'] = cur_day.strftime(day_formate)
                    content = content.append(s, ignore_index=True)
                    cur_day += timedelta(1)
            yesterday = today
        content = content.sort_values(by='day')
        content.to_csv('out.csv', index = False)
        return content    
###############################################################################    

#print(test.get_k_day('sh600660',10))
#url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz000651&scale=240&ma=no&datalen=2'


     
if __name__ == '__main__':    
    '''
    1. 先检查是否有csv或者mysql的数据，如果没有，则自动重新爬取
    2. 爬取的数据存为csv
    3. 每次获取都统一从k_day.csv一个文件中获取，没有就append进去
    '''
    test = SinaApp()
#    test.update_one('sh600660')
    
    ll = ['sh600660','sh601012','sh600377','sh000001']
    
    #更新k线数据
    test.UpdateKday(ll)
    
    #获取指定一天的数据
    a = test.GetInfo('sh600660','2019/01/08')

    #获取指定一天的价格
#    a = test.ClosePrice('sh600660','2019-01-08')

#    print(a)