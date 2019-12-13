import hashlib
import requests
import ast
import json
import websocket
import os
from urllib import request

from Client.settings import BASE_URL, SOCKET_URL


class UserApi(object):
    def __init__(self):
        """
        创建http会话对象
        """
        self.my_session = requests.session()
        self.ws = None
        self.session_id = None

    def md5_password(self, password):
        """
        对密码进行加密
        :param password: 密码
        :return:
        """
        # 创建加密对象
        md5 = hashlib.md5()
        # 对密码进行加密
        md5.update(password.encode("utf-8"))
        # 返回加密后的密码
        return md5.hexdigest()

    def get_object(self, string):
        """
        将字符串转化为对象
        :param string: 待转化的字符串
        :return:
        """
        try:
            # 将字符串转化为对象
            my_object = ast.literal_eval(string)
            # 返回字符串对象
            return my_object
        except Exception as e:
            print("字符串转字典转换失败:{}".format(e))

    def user_socket(self, user_id, receive_func):
        """
        连接socket服务器
        :param user_id: 连接的用户id
        :param receive_func: 接收消息的回调函数
        :return:
        """
        # 请求连接webSocket的url
        url = "{}user_socket/{}".format(SOCKET_URL, user_id)
        # 打开跟踪，查看日志
        websocket.enableTrace(True)

        def on_open(ws):
            """
            ws连接后的回调函数
            :param ws:
            :return:
            """
            # 封装数据
            data = {"session_id": self.session_id}
            # 发送用户验证请求数据
            self.ws.send(json.dumps(data))

        def on_message(ws, message):
            """
            ws接收到信息时的回调函数
            :param ws:
            :param message:
            :return:
            """
            # 将消息字符串转化为消息字典
            message_dict = self.get_object(message)
            # 插入消息
            receive_func(message_dict)

        def on_error(ws, error):
            """
            ws发生错误时的回调函数
            :param ws:
            :param error:
            :return:
            """
            print("socket发送错误:{}".format(error))

        def on_close(ws):
            """
            ws关闭后的回调函数
            :param ws:
            :return:
            """
            print("socket连接关闭！")

        # 连接ws
        self.ws = websocket.WebSocketApp(url, on_message=on_message,
                                         on_error=on_error,
                                         on_close=on_close,
                                         on_open=on_open, )
        # 启动ws
        self.ws.run_forever()

    def user_register(self, user_id, password):
        """
        用户注册api
        :param user_id: 用户账号
        :param password: 用户密码
        :return:
        """
        # 对密码进行加密
        password = self.md5_password(password)
        # 封装数据
        data = {
            "user_id": user_id,
            # 传输加密后的密码
            "password": password
        }
        # 拼接URL
        url = BASE_URL + "user_register"
        # 发送请求
        response = self.my_session.post(url, data=data)
        # 返回请求结果
        return response

    def user_login(self, user_id, password):
        """
        用户登录api
        :param user_id: 用户账号
        :param password: 用户密码
        :return:
        """
        # 对密码进行加密
        password = self.md5_password(password)
        # 封装数据
        data = {
            "user_id": user_id,
            # 传输加密后的密码
            "password": password
        }
        # 拼接URL
        url = BASE_URL + "user_login"
        # 发送请求
        response = self.my_session.post(url, data=data)
        try:
            # 将字符串转化为dict
            result = self.get_object(response.text)
            # 获取用户session_id
            self.session_id = result["session_id"]
            # 返回请求结果
            return result["code"]
        except Exception as e:
            print(e)
            # 返回请求结果
            return response.text

    def user_logout(self):
        """
        用户退出api
        :return:
        """
        # 拼接URL
        url = BASE_URL + "user_logout"
        # 发送请求
        response = self.my_session.get(url)
        # 返回请求结果
        return response

    def user_delete(self):
        """
        用户删除api
        :return:
        """
        # 拼接URL
        url = BASE_URL + "user_delete"
        # 发送请求
        response = self.my_session.get(url)
        # 返回请求结果
        return response

    def update_password(self, new_password):
        """
        修改用户密码api
        :param new_password: 用户新密码
        :return:
        """
        # 拼接URL
        url = BASE_URL + "update_password"
        # 对密码进行加密
        password = self.md5_password(new_password)
        # 封装数据
        data = {
            # 传输加密后的密码
            "password": password
        }
        # 发送请求
        response = self.my_session.post(url, data=data)
        # 返回请求结果
        return response

    def update_user_info(self, user_info):
        """
        修改用户信息api
        :param user_info: 用户信息
        :return:
        """
        # 拼接URL
        url = BASE_URL + "update_user_info"
        # 发送请求
        response = self.my_session.post(url, data=user_info)
        # 返回请求结果
        return response

    def download_image(self, url, image_path):
        """
        下载图片api
        :param url: 用户头像下载链接
        :param image_path: 用户头像文件保存路径
        :return:
        """
        try:
            # 补全url下载路径
            image_name = url.split("/")[-1]
            print(url)
            # 判断本地是否有用户头像文件
            if os.path.exists(image_name) is not True:
                # 下载图片
                request.urlretrieve(url=url, filename=image_path + image_name)
            # 返回图片路径
            return image_path + image_name
        except Exception as e:
            print("图片下载失败:{}".format(e))

    def upload_image(self, image_path):
        # 获取文件名
        file_name = image_path.split("/")[-1]
        # 获取文件资源
        file_bytes = open(image_path, "rb")
        # 封装数据
        files = {
            "image": (file_name, file_bytes, "image/jpg")
        }
        # 拼接URL
        url = BASE_URL + "upload_image"
        # 发送请求
        response = self.my_session.post(url, files=files)
        # 返回请求结果
        return response

    def find_user_info(self, user_id):
        """
        获取用户信息api
        :param user_id: 用户账号
        :return:
        """
        # 封装数据
        data = {
            "user_id": user_id,
        }
        # 拼接URL
        url = BASE_URL + "find_user_info"
        # 发送请求
        response = self.my_session.post(url, data=data)
        # 返回请求结果
        return response

    def delete_user_friend(self, user_id):
        """
        删除好友api
        :param user_id: 用户账号
        :return:
        """
        # 封装数据
        data = {
            "user_id": user_id,
        }
        # 拼接URL
        url = BASE_URL + "delete_user_friend"
        # 发送请求
        response = self.my_session.post(url, data=data)
        # 返回请求结果
        return response

    def find_user_friends(self):
        """
        获取用户好友api
        :return:
        """
        # 拼接URL
        url = BASE_URL + "find_user_friends"
        # 发送请求
        response = self.my_session.get(url)
        # 返回请求结果
        return response

    def find_user_friends_info(self):
        """
        获取用户好友信息api
        :return:
        """
        # 拼接URL
        url = BASE_URL + "find_user_friends_info"
        # 发送请求
        response = self.my_session.get(url)
        # 返回请求结果
        return response

    def find_user_online_info(self):
        """
        获取在线用户信息api
        :return:
        """
        # 拼接URL
        url = BASE_URL + "find_user_online_info"
        # 发送请求
        response = self.my_session.get(url)
        # 返回请求结果
        return response

    def find_all_user_info(self):
        """
        获取所有用户信息api
        :return:
        """
        # 拼接URL
        url = BASE_URL + "find_all_user_info"
        # 发送请求
        response = self.my_session.get(url)
        # 返回请求结果
        return response

    def request(self, receiver, end_url):
        """
        有关好友请求api
        :param receiver: 接受者id
        :param end_url: 末尾url
        :return:
        """
        # 封装数据
        data = {
            "receiver": receiver,
        }
        # 拼接URL
        url = BASE_URL + end_url
        # 发送请求
        response = self.my_session.post(url, data=data)
        # 返回请求结果
        return response

    def add_request(self, receiver):
        """
        发送添加好友请求api
        :param receiver: 接受者id
        :return:
        """
        # 返回请求结果
        return self.request(receiver, "add_request")

    def agree_request(self, receiver):
        """
        同意添加好友请求api
        :param receiver: 接受者id
        :return:
        """
        # 返回请求结果
        return self.request(receiver, "agree_request")

    def refuse_request(self, receiver):
        """
        拒绝添加好友请求api
        :param receiver: 接受者id
        :return:
        """
        # 返回请求结果
        return self.request(receiver, "refuse_request")

    def find_request(self):
        """
        获取用户请求api
        :return:
        """
        # 拼接URL
        url = BASE_URL + "find_request"
        # 发送请求
        response = self.my_session.get(url)
        # 返回请求结果
        return response

    def find_message_info(self):
        """
        获取用户消息通知api
        :return:
        """
        # 拼接URL
        url = BASE_URL + "find_message_info"
        # 发送请求
        response = self.my_session.get(url)
        # 返回请求结果
        return response

    def add_message(self, receiver, message):
        """
        发送消息api
        :param receiver: 接受者id
        :param message: 发送的消息
        :return:
        """
        # 封装数据
        data = {
            "receiver": receiver,
            "message": message
        }
        # 拼接URL
        url = BASE_URL + "add_message"
        # 发送请求
        response = self.my_session.post(url, data=data)
        # 返回请求结果
        return response

    def delete_message(self, sender):
        """
        删除消息api
        :param sender: 发送者id
        :return:
        """
        # 封装数据
        data = {
            "sender": sender,
        }
        # 拼接URL
        url = BASE_URL + "delete_message"
        # 发送请求
        response = self.my_session.post(url, data=data)
        # 返回请求结果
        return response

    def delete_message_info(self):
        """
        删除请求通知api
        :return:
        """
        # 拼接URL
        url = BASE_URL + "delete_message_info"
        # 发送请求
        response = self.my_session.post(url)
        # 返回请求结果
        return response

    def find_message(self):
        """
        获取用户消息api
        :return:
        """
        # 拼接URL
        url = BASE_URL + "find_message"
        # 发送请求
        response = self.my_session.get(url)
        # 返回请求结果
        return response
