from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import login_user, login_required
from flask_login import LoginManager, current_user
from urllib import parse
import os
import random
import json
import string
import time
import datetime
from datetime import datetime
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.server import WSGIServer

from Server.DB.mysql_db import MySQL
from Server.User.user_info import User
from Server.settings import SUCCESS, ERROR, SEND_REQUEST, AGREE_REQUEST, REFUSE_REQUEST, USER_NOT_EXIST, NOT_CORRECT
from Server.settings import FLASK_HOST, FLASK_PORT, ADMIN_ID, ADMIN_PASSWORD, CACHE_FILE_PATH, STATIC_PATH, ONLINE, \
    SEND_MESSAGE, ONLINE_INFO, OFFLINE_INFO
from Server.log import logger


class UserApi(object):
    def __init__(self):
        """
        初始化flask
        """
        # 创建Flask对象
        self.app = Flask(__name__)
        # 设置秘钥
        self.app.config['SECRET_KEY'] = os.urandom(24)
        # 创建数据库对象
        self.mysql = MySQL()

        # 设置用户登录管理
        self.login_manager = LoginManager()
        self.login_manager.session_protection = "strong"
        self.login_manager.login_view = "user_login"
        self.login_manager.init_app(app=self.app)

        # 保存已上线用户的socket信息
        self.login_user_dict = {}
        # 保存用户session
        self.session_user_dict = {}

        @self.login_manager.user_loader
        def load_user(user_id):
            """
            获取session中的user_id
            :param user_id: 用户账号
            :return:
            """
            return User(user_id=user_id)

        @self.app.route("/admin_login", methods=['GET', 'POST'])
        def admin_login():
            """
            管理员登录页面
            :return:
            """
            # 判断是否点击登录按钮
            if request.method == "POST":
                # 获取输入的账号密码
                user_id = request.form.get("user_id")
                password = request.form.get("password")
                # 判断账号密码是否为空
                if user_id is None or user_id is None or len(user_id) == 0 or len(password) == 0:
                    return "账号或密码都不能为空！"
                # 判断是否是管理员登录
                if user_id != ADMIN_ID or password != ADMIN_PASSWORD:
                    return "账号或密码错误！"
                # 创建用户对象
                user = User(user_id=user_id, password=password)
                # 登录用户
                login_user(user, remember=True)
                # 重定向到admin视图函数
                return redirect(url_for("admin", table="user"))
            # 返回视图文件
            return render_template("login.html")

        @self.app.route("/admin/table=<table>")
        @login_required
        def admin(table):
            """
            管理员页面
            :param table:
            :return:
            """
            # 查询表信息
            table_info_list = self.mysql.find_table_info(table)
            # 判断表信息是否为空
            if len(table_info_list) == 0:
                table_info_list = [{"NULL": "空"}]
            # 返回视图
            return render_template("admin.html", table_info_list=table_info_list)

        @self.app.route("/user_register", methods=['GET', 'POST'])
        def user_register():
            """
            用户注册
            :return:
            """
            # 判断是否是POST请求
            if request.method == "POST":
                # 获取请求参数
                request_data = request.get_data().decode("utf-8")
                # 将请求参数转化为字典
                request_dict = self._get_dict(request_data)
                # 创建用户对象
                user = User(**request_dict)
                # 往数据库中添加用户信息
                return "{}".format(self.mysql.add_user(user))
            return ERROR

        @self.app.route("/user_login", methods=['GET', 'POST'])
        def user_login():
            """
            用户登录
            :return:
            """
            # 判断是否是POST请求
            if request.method == "POST":
                # 获取请求参数
                request_data = request.get_data().decode("utf-8")
                # 将请求参数转化为字典
                request_dict = self._get_dict(request_data)
                # 创建用户对象
                user = User(**request_dict)
                # 从数据库中查找用户的信息
                result = self.mysql.find_user(user)
                # 判断查询结果是否为空
                if result is None:
                    return USER_NOT_EXIST
                # 判断请求参数中是否存在账号和密码
                if "user_id" not in result or "password" not in result:
                    return ERROR
                # 判断账号密码是否和数据库中的相同
                if user.user_id != result["user_id"] or user.password != result["password"]:
                    return NOT_CORRECT
                # 查询用户是否在线
                user_info = self.mysql.find_user_info(user)
                # 判断用户是否在线
                if user_info["online"] and user.user_id in self.login_user_dict:
                    return ONLINE
                # 登录用户
                login_user(user, remember=True)
                # 生成用户session
                session_id = ''.join(random.sample(string.ascii_letters + string.digits, 32))
                # 设置用户session
                session["session_id"] = session_id
                # 保存用户session
                self.session_user_dict[user.user_id] = session_id
                # 更新用户标记
                user.online = 1
                # 封装数据
                data = {
                    "code": self.mysql.update_user_info(user),
                    "session_id": session_id
                }
                # 从数据库中更新用户在线标记
                return "{}".format(data)
            return ERROR

        @self.app.route("/user_socket/<user_id>", methods=['GET', 'POST'])
        def user_socket(user_id):
            """
            连接webSocket客户端
            :return:
            """
            # 建立与用户客户端的连接
            client_socket = request.environ.get("wsgi.websocket")
            # 判断是否连接成功
            if client_socket is None:
                return ERROR
            # 接收用户验证请求
            request_data = client_socket.receive()
            # 将字符串转化为dict
            request_dict = json.loads(request_data)
            # 判断验证是否正确
            if request_dict["session_id"] != self.session_user_dict[user_id]:
                return ERROR
            # 将此用户加入到已登录用户列表中
            self.login_user_dict[user_id] = client_socket
            # 创建用户对象
            user = User(user_id=user_id)
            # 给好友发送上线通知
            self.send_info(user, ONLINE_INFO)
            # 监听
            while True:
                # 判断连接是否关闭
                if client_socket.closed:
                    try:
                        # 从已登录的用户中删除当前用户
                        if user_id in self.login_user_dict:
                            self.login_user_dict.pop(user_id)
                        # 从用户session中删除当前用户session
                        if user_id in self.session_user_dict:
                            self.session_user_dict.pop(user_id)
                    except Exception as e:
                        logger.exception(e)
                    break
                message = client_socket.receive()
                logger.info("{}:{}".format(user_id, message))
            return SUCCESS

        @self.app.route("/user_logout")
        @login_required
        def user_logout():
            """
            用户退出
            :return:
            """
            # 创建用户对象
            user = User(user_id=current_user.user_id)
            try:
                # 从已登录的用户中删除当前用户
                if current_user.user_id in self.login_user_dict:
                    self.login_user_dict.pop(current_user.user_id)
                # 从用户session中删除当前用户session
                if current_user.user_id in self.session_user_dict:
                    self.session_user_dict.pop(current_user.user_id)
            except Exception as e:
                logger.exception(e)
            # 给好友发送离线通知
            self.send_info(user, OFFLINE_INFO)
            # 更新用户在线标记
            user.online = 0
            # 从数据库中删除用户信息
            return "{}".format(self.mysql.update_user_info(user))

        @self.app.route("/user_delete")
        @login_required
        def user_delete():
            """
            用户删除
            :return:
            """
            # 创建用户对象
            user = User(user_id=current_user.user_id)
            # 从数据库中删除用户信息
            return "{}".format(self.mysql.delete_user(user))

        @self.app.route("/update_password", methods=['GET', 'POST'])
        @login_required
        def update_password():
            """
            修改用户密码
            :return:
            """
            # 判断是否是POST请求
            if request.method == "POST":
                # 获取请求参数
                request_data = request.get_data().decode("utf-8")
                # 将请求参数转化为字典
                request_dict = self._get_dict(request_data)
                password = request_dict["password"]
                # 创建用户对象
                user = User(user_id=current_user.user_id, password=password)
                # 从数据库中更新用户密码
                return "{}".format(self.mysql.update_password(user))
            return ERROR

        @self.app.route("/update_user_info", methods=['GET', 'POST'])
        @login_required
        def update_user_info():
            """
            修改用户信息
            :return:
            """
            # 判断是否是POST请求
            if request.method == "POST":
                # 获取请求参数
                request_data = request.get_data().decode("utf-8")
                # 将请求参数转化为字典
                request_dict = self._get_dict(request_data)
                if "info" in request_dict:
                    # 除去结尾存在多余的换行符
                    request_dict["info"] = request_dict["info"].strip()
                # 判断是否是当前用户
                if request_dict["user_id"] == current_user.user_id:
                    # 创建用户对象
                    user = User(**request_dict)
                    # 从数据库中更新用户信息
                    return "{}".format(self.mysql.update_user_info(user))
            return ERROR

        @self.app.route("/upload_image", methods=['GET', 'POST'])
        @login_required
        def upload_image():
            """
            上传用户头像
            :return:
            """
            # 判断是否是POST请求
            if request.method == "POST":
                # 获取请求参数
                request_file = request.files["image"]
                # 图片保存路径
                image_save_path = CACHE_FILE_PATH + "images/user/"
                # 将图片名设置为用户账号
                image_name = current_user.user_id + ".jpg"
                # 将用户头像保存到本地
                request_file.save(image_save_path + image_name)
                # 图片路径
                image_path = STATIC_PATH + image_name
                # 创建用户对象
                user = User(user_id=current_user.user_id, image=image_path)
                # 从数据库中更新用户信息
                return "{}".format(self.mysql.update_user_info(user))
            return ERROR

        @self.app.route("/find_user_info", methods=['GET', 'POST'])
        @login_required
        def find_user_info():
            """
            查看用户信息
            :return:
            """
            # 判断是否是POST请求
            if request.method == "POST":
                # 获取请求参数
                request_data = request.get_data().decode("utf-8")
                # 将请求参数转化为字典
                request_dict = self._get_dict(request_data)
                if "user_id" in request_dict:
                    # 创建用户对象
                    user = User(request_dict["user_id"])
                    # 从数据库中查看用户信息
                    return "{}".format(self.mysql.find_user_info(user))
                else:
                    return ERROR
            return ERROR

        @self.app.route("/delete_user_friend", methods=['GET', 'POST'])
        @login_required
        def delete_user_friend():
            """
            删除用户好友
            :return:
            """
            # 判断是否是POST请求
            if request.method == "POST":
                # 获取请求参数
                request_data = request.get_data().decode("utf-8")
                # 将请求参数转化为字典
                request_dict = self._get_dict(request_data)
                if "user_id" not in request_dict:
                    return ERROR
                # 创建用户对象
                user = User(user_id=current_user.user_id)
                # 获取好友对象
                friend = User(user_id=request_dict["user_id"])
                # 往数据库中删除用户的好友
                try:
                    self.mysql.delete_user_friend(user, friend)
                    self.mysql.delete_user_friend(friend, user)
                    return SUCCESS
                except Exception as e:
                    logger.exception(e)
                    return ERROR
            return ERROR

        @self.app.route("/find_user_friends")
        @login_required
        def find_user_friends():
            """
            查看用户好友
            :return:
            """
            # 创建用户对象
            user = User(user_id=current_user.user_id)
            # 从数据库中查看用户的好友
            user_friends_set = self.mysql.find_user_friends(user)
            return "{}".format(user_friends_set)

        @self.app.route("/find_user_friends_info")
        @login_required
        def find_user_friends_info():
            """
            查看用户好友信息
            :return:
            """
            # 创建用户对象
            user = User(user_id=current_user.user_id)
            # 从数据库中查看用户好友信息
            return "{}".format(self.mysql.find_user_friends_info(user))

        @self.app.route("/find_user_online_info")
        def find_user_online_info():
            """
            查看在线用户信息
            :return:
            """
            # 创建用户对象
            user = User(user_id=current_user.user_id)
            # 从数据库中查看在线用户信息
            return "{}".format(self.mysql.find_user_online_info(user))

        @self.app.route("/find_all_user_info")
        def find_all_user_info():
            """
            查看所有用户信息
            :return:
            """
            # 创建用户对象
            user = User(user_id=current_user.user_id)
            # 从数据库中查看在线用户信息
            return "{}".format(self.mysql.find_all_user_info(user))

        @self.app.route("/add_request", methods=['GET', 'POST'])
        @login_required
        def add_request():
            """
            发送添加好友请求
            :return:
            """
            # 判断是否是POST请求
            if request.method == "POST":
                # 获取请求参数
                request_data = request.get_data().decode("utf-8")
                # 将请求参数转化为字典
                request_dict = self._get_dict(request_data)
                # 判断数据是否存在
                if "receiver" not in request_dict:
                    return ERROR
                # 创建发送者对象
                sender = User(user_id=current_user.user_id)
                # 创建接受者对象
                receiver = User(request_dict["receiver"])
                # 封装数据
                message_dict = self._get_message_dict(sender, receiver, SEND_REQUEST)
                # 发送消息
                if self.send_message(receiver, message_dict):
                    return SUCCESS
                # 发送同意添加好友请求
                return "{}".format(self.mysql.add_message(sender, receiver, request=SEND_REQUEST))
            return ERROR

        @self.app.route("/add_message", methods=['GET', 'POST'])
        @login_required
        def add_message():
            """
            发送信息
            :return:
            """
            # 判断是否是POST请求
            if request.method == "POST":
                # 获取请求参数
                request_data = request.get_data().decode("utf-8")
                # 将请求参数转化为字典
                request_dict = self._get_dict(request_data)
                # 判断数据是否存在
                if "receiver" not in request_dict or "message" not in request_dict:
                    return ERROR
                # 创建接受者对象
                receiver = User(request_dict["receiver"])
                # 创建发送者对象
                sender = User(user_id=current_user.user_id)
                # 获取发送的信息
                message = request_dict["message"]
                # 封装数据
                message_dict = self._get_message_dict(sender, receiver, SEND_MESSAGE, message)
                # 发送消息
                if self.send_message(receiver, message_dict):
                    return SUCCESS
                # 往数据库中添加信息
                return "{}".format(self.mysql.add_message(sender, receiver, message=message))
            return ERROR

        @self.app.route("/agree_request", methods=['GET', 'POST'])
        @login_required
        def agree_request():
            """
            发送同意添加好友请求
            :return:
            """
            # 判断是否是POST请求
            if request.method == "POST":
                # 获取请求参数
                request_data = request.get_data().decode("utf-8")
                # 将请求参数转化为字典
                request_dict = self._get_dict(request_data)
                # 判断数据是否存在
                if "receiver" not in request_dict:
                    return ERROR
                # 创建发送者对象
                sender = User(user_id=current_user.user_id)
                # 创建接受者对象
                receiver = User(request_dict["receiver"])
                # 封装数据
                message_dict = self._get_message_dict(sender, receiver, AGREE_REQUEST)
                try:
                    # 发送消息
                    if self.send_message(receiver, message_dict):
                        # 删除数据库中的好友请求
                        self.mysql.delete_message(receiver, sender)
                    else:
                        # 更新数据库中的好友请求
                        self.mysql.update_request(receiver, sender, AGREE_REQUEST)
                    # 发送同意添加好友请求
                    self.mysql.add_message(sender, receiver, request=AGREE_REQUEST)
                    # 互相添加好友
                    self.mysql.add_user_friend(sender, receiver)
                    self.mysql.add_user_friend(receiver, sender)
                    return SUCCESS
                except Exception as e:
                    logger.exception(e)
                    return ERROR
            return ERROR

        @self.app.route("/refuse_request", methods=['GET', 'POST'])
        @login_required
        def refuse_request():
            """
            拒绝添加好友请求
            :return:
            """
            # 判断是否是POST请求
            if request.method == "POST":
                # 获取请求参数
                request_data = request.get_data().decode("utf-8")
                # 将请求参数转化为字典
                request_dict = self._get_dict(request_data)
                # 判断数据是否存在
                if "receiver" not in request_dict:
                    return ERROR
                # 创建发送者对象
                sender = User(user_id=current_user.user_id)
                # 创建接受者对象
                receiver = User(request_dict["receiver"])
                # 封装数据
                message_dict = self._get_message_dict(sender, receiver, REFUSE_REQUEST)
                # 发送消息
                if self.send_message(receiver, message_dict):
                    return SUCCESS
                try:
                    # 更新数据库中的好友请求
                    self.mysql.update_request(receiver, sender, REFUSE_REQUEST)
                    # 发送拒绝添加好友请求
                    self.mysql.add_message(sender, receiver, request=REFUSE_REQUEST)
                    return SUCCESS
                except Exception as e:
                    logger.exception(e)
                    return ERROR
            return ERROR

        @self.app.route("/find_request")
        @login_required
        def find_request():
            """
            查看请求
            :return:
            """
            # 创建接受者对象
            receiver = User(user_id=current_user.user_id)
            # 从数据库中查看信息
            return "{}".format(self.mysql.find_request(receiver=receiver))

        @self.app.route("/find_message_info")
        @login_required
        def find_message_info():
            """
            查看消息通知
            :return:
            """
            # 创建接受者对象
            receiver = User(user_id=current_user.user_id)
            # 从数据库中查看信息
            return "{}".format(self.mysql.find_message_info(receiver=receiver))

        @self.app.route("/delete_message", methods=['GET', 'POST'])
        @login_required
        def delete_message():
            """
            删除信息
            :return:
            """
            # 判断是否是POST请求
            if request.method == "POST":
                # 获取请求参数
                request_data = request.get_data().decode("utf-8")
                # 将请求参数转化为字典
                request_dict = self._get_dict(request_data)
                # 判断数据是否存在
                if "sender" not in request_dict:
                    return ERROR
                # 创建接受者对象
                sender = User(request_dict["sender"])
                # 创建发送者对象
                receiver = User(user_id=current_user.user_id)
                # 从数据库中删除信息
                return "{}".format(self.mysql.delete_message(sender, receiver))
            return ERROR

        @self.app.route("/delete_message_info", methods=['GET', 'POST'])
        @login_required
        def delete_message_info():
            """
            删除请求通知
            :return:
            """
            # 判断是否是POST请求
            if request.method == "POST":
                # 创建发送者对象
                receiver = User(user_id=current_user.user_id)
                # 从数据库中删除信息
                return "{}".format(self.mysql.delete_message_info(receiver))
            return ERROR

        @self.app.route("/find_message")
        @login_required
        def find_message():
            """
            查看信息
            :return:
            """
            # 创建接受者对象
            receiver = User(user_id=current_user.user_id)
            # 从数据库中查看信息
            return "{}".format(self.mysql.find_message(receiver=receiver))

    def run(self):
        """
        启动flask和wsgiServer
        :return:
        """
        # self.app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)
        http_server = WSGIServer((FLASK_HOST, FLASK_PORT), self.app, handler_class=WebSocketHandler)
        http_server.serve_forever()

    @staticmethod
    def _get_dict(request_data):
        """
        将post字符串参数转化为字典对象
        :param request_data:
        :return:
        """
        try:
            # 将请求参数进行分割
            request_data = request_data.split("&")
            # 将请求参数分割后放入字典中
            request_dict = {}
            for data in request_data:
                # 将每一个请求参数进行分割
                data = data.split("=")
                if data and len(data) >= 2:
                    # 将参数进行URL解码
                    data[0] = parse.unquote(data[0])
                    data[1] = parse.unquote(data[1])
                    # 放入字典中
                    request_dict[data[0]] = data[1]
            # 返回请求参数的字典格式
            return request_dict
        except Exception as e:
            logger.exception(e)
            return ERROR

    @staticmethod
    def _get_current_time():
        """
        获取当前系统时间
        :return:
        """
        # 获取当前时间
        current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 将时间字符串转化为时间对象
        current_date_time = datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
        return current_date_time

    def _get_message_dict(self, sender, receiver, request, message=""):
        """
        封装发送的数据
        :param sender: 发送者
        :param receiver: 接受者
        :param request: 请求类型
        :param message: 消息内容
        :return: 字典类型的数据包
        """
        message_dict = {
            "sender": sender.user_id,
            "receiver": receiver.user_id,
            "request": request,
            "message": message,
            "date_time": str(self._get_current_time())
        }
        return message_dict

    def send_message(self, receiver, message):
        """
        socket发送信息
        :param receiver: 接收者
        :param message: 消息
        :return:
        """
        # 查看接受者详细信息
        user_info = self.mysql.find_user_info(receiver)
        # 判断接受者是否在线，并且与服务端建立连接
        if user_info["online"] and receiver.user_id in self.login_user_dict and self.login_user_dict[receiver.user_id]:
            # 发送数据
            self.login_user_dict[receiver.user_id].send("{}".format(message))
            return True
        return False

    def send_info(self, user, request):
        """
        给在线好友发送上线或离线通知
        :param user: 发送者
        :param request: 请求类型
        :return:
        """
        # 获取用户好友列表
        friends_info_list = self.mysql.find_user_friends_info(user)
        # 向在线用户发送上线通知
        for friend_info in friends_info_list:
            # 判断好友是否在线
            if friend_info["online"] and friend_info["user_id"] in self.login_user_dict \
                    and self.login_user_dict[friend_info["user_id"]]:
                # 获取当前时间
                current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                # 将时间字符串转化为时间对象
                current_date_time = datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
                # 封装数据
                message_dict = {
                    "sender": user.user_id,
                    "receiver": friend_info["user_id"],
                    "request": request,
                    "message": "",
                    "date_time": str(current_date_time)
                }
                self.login_user_dict[friend_info["user_id"]].send("{}".format(message_dict))
