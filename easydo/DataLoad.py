import Data.data as data
import Mysql.mysql as mysql
if __name__ == '__main__':

    getData = data.data()
    getDatatest = getData.get_profit_data(2018,2)
    print(getDatatest)

    pushData = mysql.sql()
    