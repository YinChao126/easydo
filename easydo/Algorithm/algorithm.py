import Algorithm.stock_bond_rate as stock_bond_rate

class algorithm:

    def __init__(self):
        self.test = 0

    def GetAdvise(self, money, stock_list):
        '''
        对外输出API：输出投资建议
        输入：投资额， 目标个股
        输出：股票投资比率， 建议重点投资的股票组合
        '''
        # cur_workspace = os.getcwd()
        # sys.path.append(cur_workspace+'\Algorithm')
        # print(os.getcwd())
        # import stock_bond_rate

        rate = stock_bond_rate.GetStockRate() #获取股债比
        advise_list = stock_list[:2]
        stock_money = money * rate
        print('you should invest %d to stock' % stock_money)
        return rate, advise_list

# if __name__ == '__main__':
#     import sys
#     import os
#     BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     ALG_DIR = BASE_DIR + r'\Algorithm'
#     sys.path.append(ALG_DIR)

#     stock_list = ['600660','601012','000651','600522']
#     test = algorithm()
#     a, b = test.GetAdvise(10000, stock_list)
#     print(a, b)