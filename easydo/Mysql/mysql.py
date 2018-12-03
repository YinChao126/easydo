# -*- coding:utf-8 -*-

import os
import pymysql
from sqlalchemy import create_engine
import json
import pandas as pd


class sql:
    def __init__(self):
        self.hosts = ''
        self.users = ''
        self.passwds = ''
        self.databases = ''

    def init(self, hosts, users, passwds, databases):
        '''
    通过参数实现初始化
    '''
        self.hosts = hosts
        self.users = users
        self.passwds = passwds
        self.databases = databases

    def init_by_cfg_file(self, filenames):
        '''
    通过标准json文件实现初始化
    实际使用时，统一命名为：sql_config.json（该文件不会被托管）
    '''
        try:
            with open(filenames, 'r') as fh:
                context = fh.read()
                if context == '':
                    return -1
                else:
                    s = json.loads(context)
                    self.hosts = s['hosts']
                    self.users = s['users']
                    self.passwds = s['passwds']
                    self.databases = s['databases']
                    return 0
        except:
            print(
                "cannot open config file correctly, please check the path and try it again."
            )

    def connect(self):
        return pymysql.connect(
            host=self.hosts,
            database=self.databases,
            user=self.users,
            password=self.passwds,
            port=3306,
            charset='utf8')

    def query(self, sql):
        """
        parameter: a sql query,str
        output: a DataFrame
        """
        cnn = self.connect()
        cur = cnn.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        df = pd.DataFrame(list(result))
        cnn.commit()
        cur.close()
        cnn.close()
        return df

    def df_to_mysql(self, table, df):
        connect = create_engine("mysql+pymysql://" + self.users + ":" +
                                self.passwds + "@" + self.hosts + ":3306/" +
                                self.databases + "?charset=utf8")
        df.to_sql(
            name=table,
            con=connect,
            if_exists='append',
            index=False,
            index_label=False)


if __name__ == '__main__':

    test = sql()
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SQL_DIR = BASE_DIR + r'\Mysql'
    s = test.init_by_cfg_file(SQL_DIR + r'\sql_config.json')
    print(s)

    # Test select and output a DataFrame
    df = test.query("select * from timestampTest")
    print(df)
    A = test.query("show tables")
    print(A)
    # Test create table
    test.query("create table if not exists test2 as select * from tests")
    B = test.query("show tables")
    # Test drop table
    test.query("drop table if exists test2")
    C = test.query("show tables")
    print(B)
    print(C)

    # Test a dataFrame insert into mysql
    df = test.query("desc timestampTest")
    print(df)
    aTestDF = pd.DataFrame({"name": list("DEFGHI")})
    test.df_to_mysql("timestampTest", aTestDF)
    df = test.query("select * from timestampTest")
    print(df)

    # create a new table
    aTestDF = pd.DataFrame({"name": list("DEFGHI")})
    test.df_to_mysql("nwT", aTestDF)
    df = test.query("select * from nwT")
    print(df)