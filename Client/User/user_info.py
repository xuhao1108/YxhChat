class User(object):
    def __init__(self, user_id=None, password=None, name=None, image=None, sex=None, age=None, birthday=None, info=None,
                 online=None):
        # user:账号
        self.user_id = user_id
        # password:密码
        self.password = password
        # name:昵称
        self.name = name
        # image:头像
        self.image = image
        # sex:性别
        self.sex = sex
        # age:年龄
        self.age = age
        # birthday:生日
        self.birthday = birthday
        # info:签名
        self.info = info
        # online:在线标记
        self.online = online
