from Server.User.user_api import UserApi

if __name__ == '__main__':
    # 创建用户api对象
    user_api = UserApi()
    # 启动api
    user_api.run()
