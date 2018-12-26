'''
文档说明
'''
import os
from datetime import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from crawling_finance_table_v1_7 import crawling_finance

class M1809:
    def __init__(self,company_id_list,DataSource='SQL',LocalStore = 'ON'):
        self.company_id_list = company_id_list
        self.DataSource = DataSource
        self.LocalStore = LocalStore
        self.BasePath = '.\\easydo\\Algorithm\\M1809'
        self.HstPath = os.path.join(self.BasePath,"history_data")
        self.OutPath = os.path.join(self.BasePath,"output")

        if(DataSource !="SQL" and DataSource!='sql'):
            if (os.path.exists(self.HstPath)):
                pass
            else:
                os.mkdir(self.HstPath)
        if(LocalStore != 'OFF' and LocalStore != 'off'):
            if (os.path.exists(self.OutPath)):
                pass
            else:
                os.mkdir(self.OutPath)
        print ("History Data save in:"+self.HstPath)
        print ("Outcome Data save in:"+self.OutPath)



         

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

        if self.DataSource == 'CSV' or self.DataSource == 'csv':
            HisPath = self.BasePath+"history_data"
            if (os.path.exists(HisPath)):
                print ("Folder creation failed!")
                return
            for item in self.company_id_list:
                try:
                    file_name = os.path.join(self.HstPath,item + '_profit.csv')
                    print (file_name)
                    with open(file_name, 'r') as fh:
                        content = fh.readlines()
                        s = content[-1].split(',')
                        latest_record = parse(s[0])  #获取最新时间
                        current_day = datetime.now() - relativedelta(months=+12)
                        if latest_record > current_day:
                            pass
                        else:
                            cbfx = crawling_finance(self.HstPath, item)
                            cbfx.crawling_update()
                except Exception:
                    cbfx = crawling_finance(self.HstPath, item)
                    cbfx.crawling_update()
        else:
            test = mysql.sql()
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            SQL_DIR = BASE_DIR + r'\Mysql'
            s = test.init_by_cfg_file(SQL_DIR + r'\sql_config.json')
            # M1809_Update(cur, company_list)
        print('finish init!')
        

    # def M1809_Run(self):


if __name__ == '__main__':
    company_id_list =  ['000651', '000333', '600690']
    DataSource = "CSV"
    AObject = M1809(company_id_list,DataSource)
    AObject.M1809_Init()