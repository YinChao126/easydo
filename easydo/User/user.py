class cUser:
    
    def __init__(self, name, passwd):
        self.name = name
        self.passwd = passwd
        self.money = 0 #现有资产
        self.invest_list = [] #投资历史

    def LoadInfo(self): #辅助函数
        print('get user info from mysql')
        
    def SignOut(self, name, passwd):
        print('add a record to mysql')
    
    def Login(self, name, passwd):
        print('%s has login, passwd = %s' % (name, passwd))

    def DeleteUser(self, name, passwd):
        print('delete a user')

def user_test():
    print('just a test')

if __name__ == '__main__':
    import os
    import sys
    BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    USER_DIR = BASE_DIR + r'\User'
    sys.path.append(USER_DIR)
    test = cUser('yc', '123')
    test.Login('lilong', 'sdfgg')