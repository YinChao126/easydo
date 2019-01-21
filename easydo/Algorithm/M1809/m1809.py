# -*- coding: utf-8 -*-
'''
文档说明
'''
import os
from datetime import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from crawling_finance_table_v1_7 import crawling_finance
from CoreAnalyse import CoreAnalyse
from getData import GetData


class M1809:
    def __init__(self, company_id_list, DataSource='SQL', LocalStore='ON'):
        self.company_id_list = company_id_list
        self.DataSource = DataSource
        self.LocalStore = LocalStore
        self.BasePath = '.\\easydo\\Algorithm\\M1809'
        self.HstPath = os.path.join(self.BasePath, "history_data")  # 历史数据路径
        self.OutPath = os.path.join(self.BasePath, "output")  # 输出文档路径
        if (DataSource != "SQL" and DataSource != 'sql'):
            self.DataSource = "CSV"  # 从CSV文件中读取数据#从数据库中读取数据
            if (os.path.exists(self.HstPath)):
                pass
            else:
                os.mkdir(self.HstPath)
        else:
            self.DataSource = "SQL"  # 从数据库中读取数据
        if (LocalStore != 'OFF' and LocalStore != 'off'):
            self.LocalStore = 'ON'  # getdata数据输出到文本
            if (os.path.exists(self.OutPath)):
                pass
            else:
                os.mkdir(self.OutPath)
        else:
            self.LocalStore = 'OFF'  # 不输出到文本
        print("History Data save in:" + self.HstPath)
        print("Outcome Data save in:" + self.OutPath)

    def M1809_Init(self):
        '''
        本地模式配置
        只需要提供感兴趣的对比公司即可，如果只有一个，说明只进行自主分析
        '''
        global cur
        global parameter

        print('please wait, start init...')

        if len(self.company_id_list) < 2:
            print('最少需要输入2个id作为对比')
            return
        # 此处增加id合法性检查

        if self.DataSource == "CSV":  # 从CSV文件中读取数据
            HisPath = self.BasePath + "history_data"
            if (os.path.exists(HisPath)):
                print("Folder creation failed!")
                return
            for item in self.company_id_list:
                try:
                    file_name = os.path.join(self.HstPath,
                                             item + '_profit.csv')
                    # print (file_name)
                    with open(file_name, 'r') as fh:
                        content = fh.readlines()
                        s = content[-1].split(',')
                        latest_record = parse(s[0])  # 获取最新时间
                        current_day = datetime.now() - relativedelta(
                            months=+12)
                        if latest_record > current_day:
                            pass
                        else:
                            cbfx = crawling_finance(self.HstPath, item)
                            cbfx.crawling_update()
                except Exception:
                    cbfx = crawling_finance(self.HstPath, item)
                    cbfx.crawling_update()
        else:
            # test = mysql.sql()
            # BASE_DIR = os.path.dirname(
            #     os.path.dirname(os.path.abspath(__file__)))
            # SQL_DIR = BASE_DIR + r'\Mysql'
            # s = test.init_by_cfg_file(SQL_DIR + r'\sql_config.json')
            # M1809_Update(cur, company_list)
            pass

        print('finish init!')

    def M1809_GetData(self):
        # self_result = self.AnalyseObj.Compare2Themself(self.company_id_list[0],
        #    self.DataSource)  # 自身对比
        GetDataObj = GetData(self.DataSource, self.HstPath)
        self_result = GetDataObj.Compare2Themself(self.company_id_list[0])
        b1 = GetDataObj.Compare2Industry(self.company_id_list)  #同行业对比
        compare_result = GetDataObj.data_normalize(b1)  #归一化的同行业对比
        if self.LocalStore == 'ON':
            SelfResultPath = os.path.join(self.OutPath+'\\compare_self.csv')
            ComparePath = os.path.join(self.OutPath+'\\compare_industry.csv')
            NomalizePath = os.path.join(self.OutPath+'\\normalize.csv')

            self_result.to_csv(SelfResultPath, encoding='gbk')
            b1.to_csv(ComparePath, encoding='gbk')
            compare_result.to_csv(NomalizePath, encoding='gbk')
        return self_result, compare_result

    def M1809_Analyse(self):
        '''
        对比分析，并输出
        1. ../output/文件夹下会生成诊断报告
        2. 控制台输出对比图像（之后可以考虑保存图片）
        '''
        AnalyseObj = CoreAnalyse()
        self_result, compare_result = self.M1809_GetData()
        AnalyseObj.Analyse(self_result, compare_result,self.company_id_list[0],self.OutPath)
        AnalyseObj.PlotAnalyse(self_result)

    def M1809_Run(self):
        self.M1809_Init()
        self.M1809_Analyse()


if __name__ == '__main__':
    company_id_list = ['000651', '000333']
    DataSource = "CSV"
    AObject = M1809(company_id_list, DataSource)
    # AObject.M1809_Init()
    # self_result, compare_result= AObject.M1809_GetData()
    # print (self_result, compare_result)
    # AObject.M1809_Analyse()
    AObject.M1809_Run()