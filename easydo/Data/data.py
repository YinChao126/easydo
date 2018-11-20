import get_price

class data:
    def __init__(self):
        self.test = 0
    
    def get_yesterday_price(self, stock_id):
        return get_price.get_close_price(stock_id)

    def get_price(self, stock_id, date = 0):
        return get_price.get_close_price(stock_id, date)
    
    def get_period_k_day(self, start_day, stop_day = 0):
        '''
        获取一段时间内的k线
        '''
        return get_price.get_period_k_day(start_day, stop_day)

if __name__ == '__main__':
    import sys
    import os
    BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = BASE_DIR + r'\Data'
    sys.path.append(DATA_DIR)
    
    test = data()
    print(test.get_yesterday_price('601012'))
    print(test.get_price('601012'))
    print(test.get_period_k_day('601012','20181001'))
