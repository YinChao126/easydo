# -*- coding: utf-8 -*-

from selenium import webdriver
import os
import time
import pandas as pd
import sys

currentPath = os.path.dirname(os.path.abspath(__file__))
chromeD = currentPath + os.path.sep + "src" + os.path.sep + "chromedriver.exe"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('log-level=3')
browser = webdriver.Chrome(
    chrome_options=chrome_options, executable_path=chromeD)

browser.implicitly_wait(3)
browser.get("http://www.sse.com.cn/market/stockdata/overview/day/")

elem0 = browser.find_element_by_xpath(
    "//*[@id='tableData_934']/div[2]/table/tbody/tr[8]/td[2]/div").text
elem1 = browser.find_element_by_xpath(
    "//*[@id='tableData_934']/div[2]/table/tbody/tr[8]/td[3]/div").text
elem2 = browser.find_element_by_xpath(
    "//*[@id='tableData_934']/div[2]/table/tbody/tr[8]/td[4]/div").text

curTime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
print("{} {}".format(browser.title, curTime))
print("上海市場 换手率(%) {}".format(elem0))
print("A股 换手率(%) {}".format(elem1))
print("B股 换手率(%) {}".format(elem2))
browser.quit()

parentPath = os.path.dirname(currentPath) + os.path.sep + "Mysql"
print(parentPath)

sys.path.append(parentPath)
import mysql

dataL = []
shanghaiL = []
AL = []
BL = []
dataL.append(curTime)
shanghaiL.append(elem0)
AL.append(elem1)
BL.append(elem2)
df = pd.DataFrame({
    "日期": dataL,
    "上海市場 换手率(%)": shanghaiL,
    "A股 换手率(%)": AL,
    "B股 换手率(%)": BL
})
print(df)
# 初始化入庫模塊并數據入庫
inmysql = mysql.sql()
inmysql.init_by_cfg_file(parentPath + os.path.sep + 'sql_config.json')
inmysql.df_to_mysql("sseTurnOverRate", df)
print("完成數據入庫mysql")