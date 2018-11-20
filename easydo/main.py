import User.user
import Algorithm.algorithm as alg

if __name__ == '__main__':
    test = User.user.cUser('sss', '123')
    test.Login('s', 'a')

    adv = alg.algorithm()
    stock_list = ['600660', '601012', '000651', '600522']
    a, b = adv.GetAdvise(10000, stock_list)
    print(a, b)
