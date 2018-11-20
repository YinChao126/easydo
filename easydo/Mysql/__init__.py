import sys
import os
import pymysql
from sqlalchemy import create_engine
import json
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL_DIR = BASE_DIR + r'\Mysql'
sys.path.append(SQL_DIR)