import UserApi


id_list = ['000651', '000333', '600690', '600522']
if __name__ =='__main__':
    UserApi.Init(id_list,'SQL')
    UserApi.GetData('ON')
    UserApi.Analyse()