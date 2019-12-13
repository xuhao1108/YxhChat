from flask_login import UserMixin
import hashlib


class User(UserMixin):
    def __init__(self, user_id=None, password=None, name=None, image=None, sex=None, age=None, birthday=None, info=None,
                 online=None):
        # user:账号
        self.user_id = user_id
        self.password = password
        if password:
            # password:密码
            self.password = self.md5_password(password)
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

    def md5_password(self, password):
        # 创建加密对象
        md5 = hashlib.md5()
        # 对密码进行加密
        md5.update(password.encode("utf-8"))
        # 返回加密后的密码
        return md5.hexdigest()

    def get_id(self):
        return self.user_id
