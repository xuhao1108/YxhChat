import tkinter.messagebox
import os
import calendar
import time
import datetime
import pickle
from datetime import datetime
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

from Client.User.my_thread import MyThread
from PIL import Image, ImageTk
from Client.settings import CHAT_WIDTH, CHAT_HEIGHT, CACHE_FILE_PATH
from Client.settings import SUCCESS, ERROR, AGREE_REQUEST, REFUSE_REQUEST, SEND_REQUEST, SEND_MESSAGE, ONLINE_INFO, \
    OFFLINE_INFO


class After(object):
    """
    用户登录后的面板
    """

    def __init__(self, user_id, password, user_api):
        """
        用户登录后窗口面板初始化
        :param user_id: 用户登录的账号
        :param password: 用户登录的密码
        :param user_api: 用户登录的session会话
        """
        # 获取用户数据
        self.user_id = user_id
        self.password = password
        # 创建面板对象
        self.root = Tk()

        # 获取api连接对象
        self.user_api = user_api

        # 默认图片
        self.default_image = None
        # 按钮正常状态时的图片列表
        self.normal_photo_list = []
        # 按钮被单击状态时的图片列表
        self.click_photo_list = []
        # 按钮列表
        self.btn_list = []
        # 图片存放路径
        self.user_image_path = CACHE_FILE_PATH + "/image/user/"
        # 判断路径是否存在
        if not os.path.isdir(self.user_image_path):
            os.mkdir(self.user_image_path)

        # 消息面板
        self.mex_box = None
        # 好友消息列表
        self.friend_mes_list_box = None
        self.friend_mes_num_list_box = None
        # 用与记录当前消息行数
        self.current_line = 1
        # 显示消息的面板
        self.message_box = None
        # 消息显示区
        self.message_chat_box = None
        # 消息编辑框
        self.mes_entry = None

        # 好友面板
        self.friend_box = None
        # 好友列表
        self.friend_list = None
        self.friend_online_list = None
        # 好友详细信息
        self.friend_info = None

        # 我的面板
        self.me_box = None
        # 用户选择的图片
        self.choose_image = None
        # 详细信息面板头像
        self.detail_image = None
        # 用户选择的图片的路径
        self.choose_image_path = None

        # 记录当前点击消息列表项id,默认为0
        self.current_message_focus_id = (0,)
        # 保存用户消息列表
        self.user_message_set = set()

        # 保存用户未读消息通知列表
        self.new_message_info_list = []
        # 保存用户未读请求详细信息
        self.new_request_dict = {}
        # 保存用户未读消息字典
        self.new_message_dict = {}

        # 保存用户已读消息通知字典
        self.old_message_info_list = []
        # 保存用户已读请求详细信息
        self.old_request_dict = {}
        # 保存用户已读消息字典
        self.old_message_dict = {}

        # 读取本地聊天记录
        self.read_local_chat_record()

        # 用户好友集合
        self.find_user_friends_set = set()
        # 用户好友头像
        self.find_user_friends_image = {}
        # 用户好友详细信息
        self.find_user_friends_info_list = []
        # 用户信息标签列表
        self.user_info_label_list = {}
        # 用户信息字典转化
        self.user_info_dict = {
            'user_id': '账号',
            'name': '昵称',
            'sex': '性别',
            'age': '年龄',
            'birthday': '生日',
            'info': '简介',
            'online': '在线'
        }

        # 初始化主面板
        self.init_root()
        # 初始化按钮图片
        self.init_image_button()
        # # 初始化消息面板
        self.init_message_box()
        # # 初始化好友面板
        self.init_friend_box()
        # 初始化用户详细信息面板
        self.init_user_info_box()
        # 初始化我的面板
        self.init_me_box()

        # 默认显示好友面板
        self.btn_friend_click()

        # 创建webSocket连接
        self.create_thread(self.user_api.user_socket, self.user_id, self.receive_new_message)

        # 进入消息循环
        self.root.mainloop()

    def init_root(self):
        """
        初始化根面板
        :return:
        """
        # 设置面板标题
        self.root.title(self.user_id)
        # 计算屏幕中心位置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_width = (screen_width - CHAT_WIDTH) / 2
        center_height = (screen_height - CHAT_HEIGHT) / 2
        root_size = "%dx%d+%d+%d" % (CHAT_WIDTH, CHAT_HEIGHT, center_width, center_height)
        # 设置面板大小,并居屏幕中心
        self.root.geometry(root_size)
        # 禁止用户改变面板大小
        self.root.resizable(0, 0)
        # 设置关闭按钮点击事件
        self.root.protocol('WM_DELETE_WINDOW', self.__del__)

    def init_image_button(self):
        """
        图片按钮初始化
        :return:
        """
        # 创建图片按钮的面板
        frame = Frame(self.root)
        frame.pack()
        # 默认图片对象，若图片不能正常显示，则显示默认图片对象
        self.default_image = self.get_image(CACHE_FILE_PATH + '/image/image.png', (150, 150))
        # 创建图片按钮不被点击图片对象
        normal_image = ["mes_normal.png", "friend_normal.png", "me_normal.png"]
        normal_image_path = [CACHE_FILE_PATH + "/image/" + image for image in normal_image]
        self.normal_photo_list = [self.get_image(image, (50, 50)) for image in normal_image_path]
        # 创建图片按钮被点击图片对象
        click_image = ["mes_click.png", "friend_click.png", "me_click.png"]
        click_image_path = [CACHE_FILE_PATH + "/image/" + image for image in click_image]
        self.click_photo_list = [self.get_image(image, (50, 50)) for image in click_image_path]
        # 创建图片按钮
        btn_mes = Button(frame, text="消息", image=self.normal_photo_list[0], command=self.btn_mes_click)
        btn_mes.grid(row=0, column=0)
        btn_friend = Button(frame, text="好友", image=self.normal_photo_list[1], command=self.btn_friend_click)
        btn_friend.grid(row=0, column=1)
        btn_me = Button(frame, text="我的", image=self.normal_photo_list[2], command=self.btn_me_click)
        btn_me.grid(row=0, column=2)
        # 按钮列表
        self.btn_list = [btn_mes, btn_friend, btn_me]

    def init_message_box(self):
        """
        消息框面板初始化
        :return:
        """
        # 创建消息面板
        self.mex_box = Frame(self.root, width=CHAT_WIDTH, height=CHAT_HEIGHT - self.btn_list[0]["height"])
        self.mex_box.pack_forget()
        # 创建好友消息子面板
        label_frame = LabelFrame(self.mex_box, width=20, height=40, text="消息列表")
        label_frame.grid(row=0, column=0, sticky=N + S)
        # 创建显示消息子面板
        message_frame = Frame(self.mex_box, width=80, bd=1, relief="ridge")
        message_frame.grid(row=0, column=1, sticky=N + S)
        # 创建好友消息列表
        self.friend_mes_list_box = Listbox(label_frame, width=15, height=40, bd=0, exportselection=False,
                                           selectmode=SINGLE)
        self.friend_mes_list_box.grid(row=0, column=0)
        # 创建显示消息数目的列表
        self.friend_mes_num_list_box = Listbox(label_frame, width=5, height=40, bd=0, exportselection=False,
                                               selectmode=SINGLE)
        self.friend_mes_num_list_box.grid(row=0, column=1)
        # 插入第一条,显示好友请求
        self.friend_mes_list_box.insert(END, "通知")
        # 默认设置请求个数为空
        self.friend_mes_num_list_box.insert(END, "-")
        # 插入第一条,显示好友请求
        self.friend_mes_list_box.insert(END, "好友请求")
        # 默认设置请求个数为空
        self.friend_mes_num_list_box.insert(END, "-")
        # 绑定单击事件
        self.friend_mes_list_box.bind("<ButtonRelease-1>", self.mes_list_click)
        self.friend_mes_num_list_box.bind("<ButtonRelease-1>", self.mes_num_list_click)
        # 绑定双击事件
        # self.friend_mes_list_box.bind("<Double-Button-1>", self.mes_list_double_click)
        self.friend_mes_list_box.bind("<Button-3>", self.mes_list_double_click)
        # self.friend_mes_num_list_box.bind("<Double-Button-1>", self.mes_num_list_double_click)
        self.friend_mes_num_list_box.bind("<Button-3>", self.mes_num_list_double_click)
        # 创建显示消息的列表
        self.message_box = Listbox(message_frame, width=80)
        self.message_box.pack()
        # 绑定单击事件
        self.message_box.bind("<ButtonRelease-1>", self.message_list_click)
        # 创建消息显示区
        self.message_chat_box = Text(message_frame, width=80, state=DISABLED)
        # 绑定单击事件
        self.message_chat_box.bind("<Button-1>", self.message_chat_box_click)
        self.message_chat_box.pack_forget()
        # 创建消息编辑框
        self.mes_entry = Text(message_frame, width=80, bd=1, relief="ridge")
        # 默认不显示消息编辑框
        self.mes_entry.pack_forget()
        # 绑定回车事件
        self.mes_entry.bind("<Control-Return>", self.entry_return)
        self.mes_entry.bind("<KeyRelease-Return>", self.send_message)
        # 获取用户好友列表和好友详细信息
        self.get_message()
        # 默认选择第一项
        self.friend_mes_list_box.select_set(0)
        self.friend_mes_num_list_box.select_set(0)
        # 默认显示通知面板
        self.show_message_info_box()

    def init_friend_box(self):
        """
        好友面板初始化
        :return:
        """
        # 创建好友面板
        self.friend_box = Frame(self.root, width=CHAT_WIDTH, height=CHAT_HEIGHT - self.btn_list[0]["height"])
        self.friend_box.pack(fill="both", expand=1)
        # 创建好友列表
        label_frame = LabelFrame(self.friend_box, width=20, height=40, text="好友列表")
        label_frame.grid(row=0, column=0, sticky=N + S)
        self.friend_list = Listbox(label_frame, width=15, height=40, selectbackground="gray", bd=0,
                                   exportselection=False, selectmode=SINGLE)
        self.friend_list.grid(row=0, column=0)
        self.friend_online_list = Listbox(label_frame, width=5, height=40, selectbackground="gray", bd=0,
                                          exportselection=False, selectmode=SINGLE)

        self.friend_online_list.grid(row=0, column=1)
        # 绑定单击事件
        self.friend_list.bind("<ButtonRelease-1>", self.friend_list_click)
        self.friend_online_list.bind("<ButtonRelease-1>", self.friend_online_list_click)
        # 绑定双击事件
        # self.friend_list.bind("<Double-Button-1>", self.friend_list_double_click)
        self.friend_list.bind("<Button-3>", self.friend_list_double_click)
        # self.friend_online_list.bind("<Double-Button-1>", self.friend_online_list_double_click)
        self.friend_online_list.bind("<Button-3>", self.friend_online_list_double_click)
        # 创建好友详细信息
        self.friend_info = Frame(self.friend_box, width=CHAT_WIDTH, height=40, bd=1, relief="ridge")
        self.friend_info.grid(row=0, column=1, sticky=N + E + S + W, ipadx=CHAT_HEIGHT / 2, pady=8)
        # 获取用户好友列表和好友详细信息
        self.get_info()
        # 默认激活第一项
        self.friend_list.select_set(0)
        self.friend_online_list.select_set(0)

    def init_user_info_box(self):
        """
        用户详细信息面板初始化
        :return:
        """
        # 将信息标签添加到用户信息标签列表中
        for index, key in enumerate(self.find_user_friends_info_list[0]):
            # 判断标签是否是图片
            if key == "image":
                if self.user_id in self.find_user_friends_image:
                    # 创建图片对象
                    photo = self.find_user_friends_image[self.user_id]
                else:
                    # 创建默认图片对象
                    photo = self.default_image
                # 创建用户头像标签
                label = Label(self.friend_info, image=photo)
                # 将用户头像显示在最顶部
                label.grid(row=0, column=0, columnspan=2, padx=CHAT_WIDTH / 2 - 200)
                # 将用户头像标签添加到用户信息标签列表中
                self.user_info_label_list[key] = label
            else:
                # 创建用户信息标签
                Label(self.friend_info, text=self.user_info_dict[key] + ":").grid(row=index + 1, column=0, sticky=E + N)
                if key == "online":
                    if self.find_user_friends_info_list[0][key] == 1:
                        label = Label(self.friend_info, text="在线")
                    else:
                        label = Label(self.friend_info, text="不在线")
                else:
                    if self.find_user_friends_info_list[0][key] is None:
                        self.find_user_friends_info_list[0][key] = " "
                    label = Label(self.friend_info, wraplength=200, justify='left',
                                  text=self.find_user_friends_info_list[0][key])
                label.grid(row=index + 1, column=1, sticky=W)
                # 将用户信息标签添加到用户信息标签列表中
                self.user_info_label_list[key] = label

    def init_me_box(self):
        """
        我的面板初始化
        :return:
        """
        # 创建我的面板
        self.me_box = Frame(self.root, width=CHAT_WIDTH, height=CHAT_HEIGHT - self.btn_list[0]["height"])
        self.me_box.pack_forget()
        # 创建放置按钮的子容器
        me_btn_box = Frame(self.me_box)
        me_btn_box.place(x=CHAT_WIDTH / 2, y=0, anchor=N)
        # 创建修改信息按钮
        Button(me_btn_box, width=10, height=2, text="修改信息", command=self.btn_update_info).grid(row=0, column=0)
        # 创建修改头像按钮
        Button(me_btn_box, width=10, height=2, text="修改头像", command=self.btn_update_image).grid(row=0, column=1)
        # 创建修改密码按钮
        Button(me_btn_box, width=10, height=2, text="修改密码", command=self.btn_update_password).grid(row=1, column=0)
        # 创建添加好友按钮
        Button(me_btn_box, width=10, height=2, text="添加好友", command=self.btn_add_friend).grid(row=1, column=1)
        # 创建退出登录按钮
        Button(me_btn_box, width=10, height=2, text="退出登录", command=self.btn_logout_user).grid(row=2, column=0)
        # 创建注销用户按钮
        Button(me_btn_box, width=10, height=2, text="删除此用户", command=self.btn_delete_user).grid(row=2, column=1)

    def init_top(self, title, width, height):
        """
        创建顶部对象
        :param title: 顶部对象标题
        :param width: 顶部对象宽度
        :param height: 顶部对象高度
        :return:
        """
        # 创建顶部面板
        top = Toplevel(self.root)
        # 设置顶部面板标题
        top.title(title)
        # 计算顶部面板居中位置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_width = (screen_width - width) / 2
        center_height = (screen_height - height) / 2
        # 设置面板大小,并居屏幕中心
        root_size = "%dx%d+%d+%d" % (width, height, center_width, center_height)
        # 设置顶部面板大小并居中
        top.geometry(root_size)
        return top

    def read_local_chat_record(self):
        try:
            # 若不存在则会抛出异常
            with open(CACHE_FILE_PATH + "/chat_record.pkl", "rb") as file:
                # 获取本地存储的用户信息
                chat_record = pickle.load(file)
                # 获取本地未已读信息
                self.old_message_info_list = chat_record["old_message_info_list"]
                self.old_request_dict = chat_record["old_request_dict"]
                self.old_message_dict = chat_record["old_message_dict"]
        except Exception as e:
            print("文件chat_record.pkl不存在:{}".format(e))

    def format_text(self, *args, length=20):
        """
        格式化字符串
        :param length: 需要格式化的长度
        :param args: 需要格式化的参数
        :return:
        """
        # 拼接格式化字符串
        format_type = ""
        for index in range(len(args)):
            format_type += "{" + str(index) + ":{" + str(len(args)) + "}^" + str(length) + "}\t"
        return format_type.format(*args, chr(12288))

    def format_date(self, date):
        """
        格式化日期
        :param date: 需要格式化的日期
        :return:
        """
        # 获取当前时间
        current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 将时间字符串转化为时间对象
        format_date_time = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        current_date_time = datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
        # 获取当前月日
        new_date = str(format_date_time.month) + "." + str(format_date_time.day)
        # 获取当前时分
        new_time = str(format_date_time.hour) + ":" + str(format_date_time.minute)
        # 判断年份是否相同
        if format_date_time.year == current_date_time.year:
            # 判断月份是否相同
            if format_date_time.month == current_date_time.month:
                # 判断日期是否相同
                if format_date_time.day == current_date_time.day:
                    return new_time
            return new_date + "    " + new_time
        return date

    def receive_new_message(self, message):
        """
        socket接收新消息的回调函数
        :param message: 接收到的消息
        :return:
        """
        # 获取用户详细信息
        response = self.create_thread(self.user_api.find_user_info, message["sender"])
        sender_user_info = self.user_api.get_object(response.text)
        # 将用户昵称添加到请求字典中
        message["name"] = sender_user_info["name"]
        # 判断信息类型
        if message["request"] != SEND_REQUEST and message["request"] != SEND_MESSAGE:
            if message["request"] == ONLINE_INFO or message["request"] == OFFLINE_INFO:
                # 更新用户在线标记
                # 将发送者格式与好友列表格式保持一致:昵称+"("+用户id+")"
                sender_item = sender_user_info["name"] + "(" + sender_user_info["user_id"] + ")"
                # 获取好友列表
                friend_list = self.friend_list.get(0, END)
                # 判断发送者是否在好友列表中
                if message["sender"] in friend_list:
                    # 获取该用户所在位置
                    index = friend_list.index(sender_item)
                    # 将用户更新为在线
                    self.friend_online_list.delete(index, index)
                    if message["request"] == ONLINE_INFO:
                        self.friend_online_list.insert(index, "在线")
                    elif message["request"] == ONLINE_INFO:
                        self.friend_online_list.insert(index, "离线")
            # 将消息添加到用户未读消息通知字典中
            self.new_message_info_list.append(message)
            # 更新面板
            self.friend_mes_num_list_box.delete(0, 0)
            # 向面板中插入新通知的个数
            self.friend_mes_num_list_box.insert(0, len(self.new_message_info_list))
            # 判断当前面板是否是请求消息面板
            if 0 in self.current_message_focus_id:
                # 向请求消息面板中插入新消息
                self.insert_message_info(message)
            # 判断是否是同意添加好友，若是同意添加好友，则更新好友面板
            if message["request"] == AGREE_REQUEST:
                # 更新好友集合和好友面板
                self.insert_new_friend(message["sender"])
        elif message["request"] == SEND_REQUEST:
            # 将消息添加到用户未读请求详细信息中
            self.new_request_dict[sender_user_info["user_id"]] = message
            # 更新面板
            self.friend_mes_num_list_box.delete(1, 1)
            # 向面板中插入新请求的个数
            self.friend_mes_num_list_box.insert(1, len(self.new_request_dict))
            # 判断当前面板是否是请求面板
            if 1 in self.current_message_focus_id:
                # 向请求面板中插入新消息
                self.insert_request(message)
        elif message["request"] == SEND_MESSAGE:
            # 将当前用户添加到消息列表中
            self.user_message_set.add(message["sender"])
            # 判断未读消息中是否存在该用户
            if message["sender"] not in self.new_message_dict:
                # 创建该用户的消息列表
                self.new_message_dict[message["sender"]] = []
            # 将消息添加到用户未读消息字典中
            self.new_message_dict[message["sender"]].append(message)
            # 获取消息列表
            mes_list = self.friend_mes_list_box.get(0, END)
            # 将发送者格式与消息列表格式保持一致:昵称+"("+用户id+")"
            sender_item = sender_user_info["name"] + "(" + sender_user_info["user_id"] + ")"
            # 获取被单击的列表项
            select_item = self.friend_mes_list_box.get(self.current_message_focus_id)
            # 是否更新选中项id的标记
            update_focus_flag = 0
            # 判断是否需要更新当前选中id
            update_current_id = 1
            # 判断当前消息面板用户是否与发送者一致
            if sender_item == select_item:
                # 更新标记
                update_focus_flag = 1
            # 判断消息列表中是否存在改用户
            if sender_item in mes_list:
                # 获取该用户所在位置
                index = mes_list.index(sender_item)
                # 将该用户从消息列表中删除
                self.friend_mes_list_box.delete(index, index)
                self.friend_mes_num_list_box.delete(index, index)
                # 判断当前删除项是否在被点击项后边
                if index < self.current_message_focus_id[0]:
                    # 更新标记
                    update_current_id = 0
                # 向消息列表中添加此消息用户
            self.friend_mes_list_box.insert(2, sender_item)
            # 判断数据是否为空
            if message["sender"] in self.new_message_dict:
                message_length = len(self.new_message_dict[message["sender"]])
            else:
                message_length = "1"
                self.new_message_dict[message["sender"]] = []
                self.new_message_dict[message["sender"]].append(message)
            self.friend_mes_num_list_box.insert(2, message_length)
            # 判断是否是否需要更新选中项id
            if update_focus_flag:
                # 更新当前消息列表选中项
                self.current_message_focus_id = (2,)
                # 更新选中项
                self.friend_mes_list_box.selection_clear(0, END)
                self.friend_mes_num_list_box.selection_clear(0, END)
                self.friend_mes_list_box.select_set(2)
                self.friend_mes_num_list_box.select_set(2)
                # 更新聊天面板
                self.insert_message(message)
            elif update_current_id:
                # 更新当前消息列表选中项
                self.current_message_focus_id = (self.current_message_focus_id[0] + 1,)
                # 更新选中项
                self.friend_mes_list_box.selection_clear(0, END)
                self.friend_mes_num_list_box.selection_clear(0, END)
                self.friend_mes_list_box.select_set(self.current_message_focus_id)
                self.friend_mes_num_list_box.select_set(self.current_message_focus_id)

    def get_message(self):
        """
        获取用户消息列表
        :return:
        """
        # 获取用户通知
        response = self.create_thread(self.user_api.find_message_info)
        find_message_info = self.user_api.get_object(response.text)
        # 判断数据是否为空
        if find_message_info is None:
            find_message_info = []
        # 获取用户请求
        response = self.create_thread(self.user_api.find_request)
        find_request = self.user_api.get_object(response.text)
        # 判断数据是否为空
        if find_request is None:
            find_request = []
        # 获取用户消息列表
        response = self.create_thread(self.user_api.find_message)
        find_message = self.user_api.get_object(response.text)
        # 判断数据是否为空
        if find_message is None:
            find_message = []
        # 清空面板
        self.friend_mes_num_list_box.delete(0, 1)
        # 插入通知和请求
        self.friend_mes_num_list_box.insert(0, len(find_message_info))
        self.friend_mes_num_list_box.insert(1, len(find_request))
        # 将好友请求通知依次添加到请求面板中
        for message_info in find_message_info:
            # 获取用户详细信息
            response = self.create_thread(self.user_api.find_user_info, message_info["sender"])
            find_user_info = self.user_api.get_object(response.text)
            # 将用户昵称添加到请求信息中
            message_info["name"] = find_user_info["name"]
            # 将请求通知信息添加到用户未读消息通知列表中
            self.new_message_info_list.append(message_info)
        # 将好友请求依次添加到请求面板中
        for request in find_request:
            # 获取用户详细信息
            response = self.create_thread(self.user_api.find_user_info, request["sender"])
            find_user_info = self.user_api.get_object(response.text)
            # 将用户昵称添加到请求信息中
            request["name"] = find_user_info["name"]
            # 将请求信息添加到用户未读请求字典中
            self.new_request_dict[find_user_info["user_id"]] = request
        # 将用户消息依次添加到消息dict中
        for message in find_message:
            # 判断消息dict中是否存在次用户的消息
            if message["sender"] not in self.new_message_dict:
                # 获取用户详细信息
                self.new_message_dict[message["sender"]] = []
            self.new_message_dict[message["sender"]].append(message)
        # 将未读消息用户添加到用户消息集合中
        for user_id in self.new_message_dict:
            self.user_message_set.add(user_id)
        # 将已读消息用户添加到用户消息集合中
        for user_id in self.old_message_dict:
            self.user_message_set.add(user_id)
        # 依次将消息显示到面板上
        for user_id in self.user_message_set:
            # 获取用户详细信息
            response = self.create_thread(self.user_api.find_user_info, user_id)
            find_user_info = self.user_api.get_object(response.text)
            if find_user_info:
                # 将消息和消息个数显示到面板上
                self.friend_mes_list_box.insert(END, find_user_info["name"] + "(" + user_id + ")")
                # 判断是否有新消息
                if user_id in self.new_message_dict:
                    length = len(self.new_message_dict[user_id])
                else:
                    length = " "
                    self.new_message_dict[user_id] = []
                self.friend_mes_num_list_box.insert(END, length)

    def get_info(self, select_id=None):
        """
        获取用户信息，好友列表，好友信息，下载好友图片
        :param select_id: 选中项id
        :return:
        """
        # 获取用户详细信息
        response = self.create_thread(self.user_api.find_user_info, self.user_id)
        find_user_info = self.user_api.get_object(response.text)
        # 获取用户好友集合
        response = self.create_thread(self.user_api.find_user_friends)
        self.find_user_friends_set = self.user_api.get_object(response.text)
        # 判断好友列表是否为空
        if self.find_user_friends_set is None:
            self.find_user_friends_set = set()
        # 将用户本人添加到集合中
        self.find_user_friends_set.add(self.user_id)
        # 获取用户好友详细信息列表
        response = self.create_thread(self.user_api.find_user_friends_info)
        # 获取用户好友信息
        self.find_user_friends_info_list = self.user_api.get_object(response.text)
        # 将用户好友详细信息添加到用户好友详细信息列表首位
        self.find_user_friends_info_list.insert(0, find_user_info)
        # 将好友头像下载到本地
        for friend in self.find_user_friends_info_list:
            # 判断用户是否有头像
            if friend["image"]:
                # 下载用户头像
                image_path = self.create_thread(self.user_api.download_image, friend["image"], self.user_image_path)
                # 更新用户头像
                self.find_user_friends_image[friend["user_id"]] = self.get_image(image_path, (150, 150))
            else:
                self.find_user_friends_image[friend["user_id"]] = None
        # 将列表面板清空
        self.friend_list.delete(0, END)
        self.friend_online_list.delete(0, END)
        # 将用户好友依次添加到用户好友面板中
        for friend in self.find_user_friends_info_list:
            self.friend_list.insert(END, friend["name"] + "(" + friend["user_id"] + ")")
            online = "在线" if friend["online"] else "离线"
            self.friend_online_list.insert(END, online)
        # 判断是否有默认选中项
        if select_id:
            # 激活默认选择项
            self.friend_list.selection_clear(0, END)
            self.friend_online_list.selection_clear(0, END)
            self.friend_list.select_set(select_id)
            self.friend_online_list.select_set(select_id)

    def get_image(self, file_path, size):
        """
        获取图片对象
        :param file_path:图片路径
        :param size:图片缩放尺寸
        :return:
        """
        if file_path and os.path.isfile(file_path):
            # 打开图片
            image = Image.open(file_path)
            # 将图片缩放为150*150
            image.thumbnail(size)
            # 创建图片按钮对象
            photo = ImageTk.PhotoImage(image)
            return photo

    def get_day(self, event, year, month, day, age):
        """
        计算当前月份有多少天
        :param event:触发事件需event参数
        :param year:存放年的变量
        :param month:存放月的变量
        :param day:存放日的变量
        :param age:显示年龄的控件
        :return:
        """
        # 获取当前选中的年月
        select_year = year.get()
        select_month = month.get()
        select_day = day.get()
        if select_year and select_month:
            select_year = int(select_year)
            select_month = int(select_month)
            # 获取当前年月的天数
            month_day = calendar.monthrange(select_year, select_month)
            # 设置天数
            day["value"] = tuple([i for i in range(1, month_day[1] + 1)])
            # 若生日选择完毕,则计算当前年龄
            if day:
                # 获取出生日期
                select_day = int(select_day)
                # 获取今天日期
                today = datetime.datetime.today()
                # 获取出生日期
                born = datetime.date(select_year, select_month, select_day)
                # 计算年龄
                my_age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
                my_age = my_age if my_age > 0 else 0
                # 设置年龄
                age.set(my_age)

    def set_image_type(self, btn_id):
        """
        设置图片状态，正常状态与被单击状态
        :param btn_id: 被单击按钮id
        :return:
        """
        # 将所有按钮设置为正常状态
        for index, btn in enumerate(self.btn_list):
            btn["image"] = self.normal_photo_list[index]
        # 将被单击按钮设置为单击状态图片
        self.btn_list[btn_id]["image"] = self.click_photo_list[btn_id]

        # 设置所有面板不可见
        box_list = [self.mex_box, self.friend_box, self.me_box]
        for box in box_list:
            box.pack_forget()
        # 设置被单击按钮面板可见
        box_list[btn_id].pack(fill="both", expand=1)

    def btn_mes_click(self):
        """
        消息按钮单击事件
        :return:
        """
        # 设置按钮被单击状态的图标
        self.set_image_type(0)

    def mes_list_click(self, event):
        """
        消息列表单击事件
        :param event: 事件参数
        :return:
        """
        # 获取被单击的列表项id
        select_id = self.friend_mes_list_box.curselection()
        # 更新当前点击消息列表项id
        self.current_message_focus_id = select_id
        # 关联被单击项
        self.friend_mes_num_list_box.selection_clear(0, END)
        self.friend_mes_num_list_box.selection_set(select_id)
        # 获取被单击的列表项用户id
        select_user_item = self.friend_mes_list_box.get(select_id)
        index_start = select_user_item.rfind("(")
        index_stop = select_user_item.rfind(")")
        select_user_id = select_user_item[index_start + 1:index_stop]
        # 将被单击项未读消息重置为0
        self.friend_mes_num_list_box.delete(select_id, select_id)
        self.friend_mes_num_list_box.insert(select_id, " ")
        # 判断是否是好友请求面板
        if 0 in select_id:
            # 将信息显示到面板上
            self.show_message_info_box()
            # 将未读消息通知添加到已读消息通知中
            for message_info in self.new_message_info_list:
                self.old_message_info_list.append(message_info)
            # 清空未读消息通知
            self.new_message_info_list = []
            # 删除已读消息通知
            self.create_thread(self.user_api.delete_message_info)
        elif 1 in select_id:
            # 将信息显示到面板上
            self.show_request_box()
            # 将未读消息通知添加到已读消息通知中
            for user_id in self.new_request_dict:
                self.old_request_dict[user_id] = self.new_request_dict[user_id]
            # 清空未读消息通知
            self.new_request_dict = {}
        else:
            # 判断消息中是否有此用户的键
            if select_user_id not in self.new_message_dict:
                self.new_message_dict[select_user_id] = []
            if select_user_id not in self.old_message_dict:
                self.old_message_dict[select_user_id] = []
            # 将信息显示到面板上
            self.show_message_box(select_user_id)
            # 将未读消息通知添加到已读消息通知中
            for user_id in self.new_message_dict[select_user_id]:
                self.old_message_dict[select_user_id].append(user_id)
            # 清空未读消息通知
            self.new_message_dict[select_user_id] = []
            # 删除已读消息通知
            self.create_thread(self.user_api.delete_message, select_user_id)

    def mes_num_list_click(self, event):
        """
        消息列表单击事件
        :param event: 事件参数
        :return:
        """
        # 获取被单击的列表项id
        select_id = self.friend_mes_num_list_box.curselection()
        # 关联被单击项
        self.friend_mes_list_box.selection_clear(0, END)
        self.friend_mes_list_box.selection_set(select_id)
        # 显示点击项的详细信息
        self.mes_list_click(event)

    def mes_list_double_click(self, event):
        """
        消息列表双击事件
        :param event: 事件参数
        :return:
        """
        # 获取被单击的列表项id
        select_id = self.friend_mes_list_box.curselection()
        # 关联被单击项
        self.friend_mes_num_list_box.selection_clear(0, END)
        self.friend_mes_num_list_box.selection_set(select_id)
        # 获取被单击的列表项
        select_item = self.friend_mes_list_box.get(select_id)
        # 获取被单击的列表项用户id
        index_start = select_item.rfind("(")
        index_stop = select_item.rfind(")")
        select_user_id = select_item[index_start + 1:index_stop]
        # 创建菜单
        menu = Menu(self.friend_list, tearoff=0)
        # 判断被单击项是否是用户
        if 0 not in select_id and 1 not in select_id:
            # 添加菜单项
            menu.add_command(label="删除信息", command=lambda: self.delete_message(select_id, select_user_id))
            menu.add_separator()
            menu.add_command(label="查看详细信息", command=lambda: self.show_user_info(select_user_id))
        # 将菜单面板放置在鼠标处
        menu.post(x=event.x_root, y=event.y_root)

    def mes_num_list_double_click(self, event):
        """
        消息列表双击事件
        :param event: 事件参数
        :return:
        """
        # 获取被单击的列表项id
        select_id = self.friend_mes_num_list_box.curselection()
        # 关联被单击项
        self.friend_mes_list_box.selection_clear(0, END)
        self.friend_mes_list_box.selection_set(select_id)
        # 显示点击项的详细信息
        self.mes_list_double_click(event)

    def show_message_info_box(self):
        """
        显示通知面板
        :return:
        """
        # 显示消息通知面板,不显示消息编辑区
        self.message_box.pack_forget()
        self.message_chat_box.pack_forget()
        self.mes_entry.pack_forget()
        self.message_box.pack(side=TOP, fill=BOTH, expand=YES)
        # 字符串格式化对齐
        text1 = self.format_text("通知", length=50)
        text2 = self.format_text("通知", "时间", length=20)
        # 清空面板
        self.message_box.delete(0, END)
        # 插入表头信息
        self.message_box.insert(END, text1)
        self.message_box.insert(END, text2)
        # 将未读消息通知依次显示到面板上
        for message_info in self.new_message_info_list:
            self.insert_message_info(message_info)
        # 将已读消息通知依次显示到面板上
        for message_info in self.old_message_info_list:
            self.insert_message_info(message_info)

    def insert_message_info(self, message_info):
        """
        向请求消息面板中插入信息
        :param message_info: 消息信息
        :return:
        """
        if message_info["request"] == AGREE_REQUEST:
            info = "{}({})同意添加您为好友!".format(message_info["name"], message_info["sender"])
        elif message_info["request"] == REFUSE_REQUEST:
            info = "{}({})拒绝添加您为好友!".format(message_info["name"], message_info["sender"])
        elif message_info["request"] == ONLINE_INFO:
            info = "{}({})上线了!".format(message_info["name"], message_info["sender"])
        elif message_info["request"] == OFFLINE_INFO:
            info = "{}({})下线了!".format(message_info["name"], message_info["sender"])
        else:
            info = "-.-"
        # 格式化显示时间
        date_time = self.format_date(message_info["date_time"])
        # 字符串格式化对齐
        text = self.format_text(info, date_time, length=25)
        # 将通知信息显示到面板上
        self.message_box.insert(END, text)

    def show_request_box(self):
        """
        显示请求面板
        :return:
        """
        # 显示消息通知面板,不显示消息编辑区
        self.message_box.pack_forget()
        self.message_chat_box.pack_forget()
        self.mes_entry.pack_forget()
        self.message_box.pack(side=TOP, fill=BOTH, expand=YES)
        # 字符串格式化对齐
        text1 = self.format_text("添加好友请求", length=50)
        text2 = self.format_text("账号", "昵称", "时间", length=14)
        # 清空面板
        self.message_box.delete(0, END)
        # 插入表头信息
        self.message_box.insert(END, text1)
        self.message_box.insert(END, text2)
        # 将未读消息通知依次显示到面板上
        for user_id, request_info in self.new_request_dict.items():
            self.insert_request(request_info)
        # 将已读消息通知依次显示到面板上
        for user_id, request_info in self.old_request_dict.items():
            self.insert_request(request_info)

    def insert_request(self, request_info):
        """
        向请求面板中插入信息
        :param request_info: 消息信息
        :return:
        """
        # 格式化显示时间
        date_time = self.format_date(request_info["date_time"])
        # 字符串格式化对齐
        text = self.format_text(request_info["sender"], request_info["name"], date_time, length=15)
        # 将通知信息显示到面板上
        self.message_box.insert(END, text)

    def show_message_box(self, select_user_id):
        """
        显示消息面板
        :param select_user_id: 选中的用户id
        :return:
        """
        # 显示消息通知面板和消息编辑区
        self.message_box.pack_forget()
        self.message_chat_box.pack_forget()
        self.mes_entry.pack_forget()
        self.message_chat_box["width"] = 100
        self.mes_entry["width"] = 100
        self.message_chat_box.pack(side=TOP, fill=BOTH, expand=YES)
        self.mes_entry.pack(side=TOP, fill=BOTH, expand=YES)
        # 设置面板为可以修改
        self.message_chat_box["state"] = NORMAL
        # 当前行数
        self.current_line = 1
        # 清空面板
        self.message_chat_box.delete("1.0", END)
        # 创建显示表头信息的控件
        friend_label = Label(self.message_chat_box, text=select_user_id)
        # 将表头信息显示到面板上
        self.message_chat_box.window_create(END, window=friend_label)
        # 设置标记
        self.message_chat_box.tag_add("header", str(self.current_line) + ".0", str(self.current_line) + ".end")
        self.message_chat_box.tag_config("header", justify=CENTER)
        # 插入换行
        self.message_chat_box.insert(END, "\n")
        # 当前行数+1
        self.current_line += 1
        # 设置面板为禁止修改
        self.message_chat_box["state"] = DISABLED
        # 判断未读消息中是否存在该用户的消息
        if select_user_id not in self.new_message_dict:
            self.new_message_dict[select_user_id] = []
        # 将未读消息通知依次显示到面板上
        for message in self.new_message_dict[select_user_id]:
            # 将消息插入到面板
            self.insert_message(message)
        # 判断已读消息中是否存在该用户的消息
        if select_user_id not in self.old_message_dict:
            self.old_message_dict[select_user_id] = []
        # 将已读消息通知依次显示到面板上
        for message in self.old_message_dict[select_user_id]:
            # 将消息插入到面板
            self.insert_message(message)

    def insert_message(self, message):
        """
        向消息面板中插入信息
        :param message: 消息信息
        :return:
        """
        # 设置面板为可以修改
        self.message_chat_box["state"] = NORMAL
        # 格式化显示时间
        date_time = self.format_date(message["date_time"])
        # 创建显示时间的控件
        time_label = Label(self.message_chat_box, text=date_time)
        # 将通知信息显示到面板上
        self.message_chat_box.window_create(INSERT, window=time_label)
        # 设置标记
        self.message_chat_box.tag_add("time", str(self.current_line) + ".0", str(self.current_line) + ".end")
        self.message_chat_box.tag_config("time", justify=CENTER)
        # 插入换行
        self.message_chat_box.insert(INSERT, "\n")
        # 当前行数+1
        self.current_line += 1
        # 创建显示消息的控件
        message_label = Label(self.message_chat_box, text=message["message"], bg="blue", wraplength=200)
        # 将通知信息显示到面板上
        self.message_chat_box.window_create(INSERT, window=message_label)
        # 判断消息类型
        if message["sender"] != self.user_id:
            # 设置标记
            self.message_chat_box.tag_add("friend", str(self.current_line) + ".0", str(self.current_line) + ".end")
            self.message_chat_box.tag_config("friend", justify=LEFT)
        else:
            message_label["bg"] = "green"
            # 设置标记
            self.message_chat_box.tag_add("me", str(self.current_line) + ".0", str(self.current_line) + ".end")
            self.message_chat_box.tag_config("me", justify=RIGHT)
        # 插入换行
        self.message_chat_box.insert(INSERT, "\n")
        # 当前行数+1
        self.current_line += 1
        # 设置面板为禁止修改
        self.message_chat_box["state"] = DISABLED

    def delete_message(self, select_id, select_user_id):
        """
        删除消息菜单项单击事件
        :param select_id: 选中的列表id
        :param select_user_id: 选中的用户id
        :return:
        """
        # 从消息列表中删除被单击项
        self.friend_mes_list_box.delete(select_id, select_id)
        self.friend_mes_num_list_box.delete(select_id, select_id)
        # 将未读消息删除，并添加到已读消息中
        message_list = self.new_message_dict.pop(select_user_id)
        # 判断已读消息中是否存在此用户的信息
        if select_user_id not in self.old_message_dict:
            self.old_message_dict[select_user_id] = []
        # 依次将未读消息添加到已读消息中
        for message in message_list:
            self.old_message_dict[select_user_id].append(message)
        # 删除已读消息通知
        self.create_thread(self.user_api.delete_message, select_user_id)
        # 删除后默认激活第一项
        self.friend_mes_list_box.selection_clear(0, END)
        self.friend_mes_num_list_box.selection_clear(0, END)
        self.friend_mes_list_box.select_set(0)
        self.friend_mes_num_list_box.select_set(0)

    def message_list_click(self, event):
        """
        消息列表单击事件
        :param event: 事件参数
        :return:
        """
        # 获取被单击的列表项id
        select_id = self.message_box.curselection()
        if 0 in self.current_message_focus_id:
            # 判断是否是表头
            if 0 in select_id or 1 in select_id:
                return
            # 创建菜单
            menu = Menu(self.message_box, tearoff=0)
            # 获取被单击的列表项用户id
            select_user_item = self.message_box.get(select_id)
            index_start = select_user_item.rfind("(")
            index_stop = select_user_item.rfind(")")
            select_user_id = select_user_item[index_start + 1:index_stop]
            # 添加菜单项
            menu.add_command(label="查看信息", command=lambda: self.show_user_info(select_user_id))
            menu.add_separator()
            menu.add_command(label="清空记录", command=lambda: self.clear_chat_record())
            # 将菜单面板放置在鼠标处
            menu.post(x=event.x_root, y=event.y_root)
        elif 1 in self.current_message_focus_id:
            # 判断是否是表头
            if 0 in select_id or 1 in select_id:
                return
            # 创建菜单
            menu = Menu(self.message_box, tearoff=0)
            # 获取被单击的列表项用户id和用户昵称
            select_item = self.message_box.get(select_id)
            split_result = re.findall(r"\w+", select_item)
            select_user_id = split_result[0] if len(split_result) > 0 else None
            # 添加菜单项
            menu.add_command(label="同意添加好友", command=lambda: self.agree_request(select_id, select_user_id))
            menu.add_separator()
            menu.add_command(label="拒绝添加好友", command=lambda: self.refuse_request(select_id, select_user_id))
            menu.add_separator()
            menu.add_command(label="查看信息", command=lambda: self.show_user_info(select_user_id))
            menu.add_separator()
            menu.add_command(label="清空记录", command=lambda: self.clear_chat_record())
            # 将菜单面板放置在鼠标处
            menu.post(x=event.x_root, y=event.y_root)

    def agree_request(self, select_id, select_user_id):
        """
        同意添加好友菜单项点击事件
        :param select_id: 选中项id
        :param select_user_id: 选中的用户id
        :return:
        """
        # 发送请求
        response = self.create_thread(self.user_api.agree_request, select_user_id)
        if response.text == SUCCESS:
            tkinter.messagebox.showinfo("成功了", message="好友添加成功！")
            # 更新好友集合和好友面板
            self.insert_new_friend(select_user_id)
            # 删除此请求项
            self.message_box.delete(select_id, select_id)
            # 从未读消息中删除此请求项
            if select_user_id in self.new_request_dict:
                self.new_request_dict.pop(select_user_id)
            # 从已读消息中删除此请求项
            if select_user_id in self.old_request_dict:
                self.old_request_dict.pop(select_user_id)
        elif response.text == ERROR:
            tkinter.messagebox.showinfo("成功了", message="好友添加失败！")
            # 销毁面板

    def insert_new_friend(self, select_user_id):
        """
        将新好友添加到好友集合中，并更新面板
        :param select_user_id: 选中用户id
        :return:
        """
        # 判断新好友是否在好友集合中存在
        if select_user_id not in self.find_user_friends_set:
            # 将新好友添加到好友列表中
            self.find_user_friends_set.add(select_user_id)
            # 获取用户详细信息
            response = self.create_thread(self.user_api.find_user_info, select_user_id)
            find_user_info = self.user_api.get_object(response.text)
            self.find_user_friends_info_list.append(find_user_info)
            # 下载用户头像
            if find_user_info["image"]:
                # 下载头像
                image_path = self.create_thread(self.user_api.download_image, find_user_info["image"],
                                                self.user_image_path)
                # 更新用户头像
                self.find_user_friends_image[select_user_id] = self.get_image(image_path, (150, 150))
            else:
                self.find_user_friends_image[select_user_id] = None
            # 将列表面板清空
            self.friend_list.delete(0, END)
            self.friend_online_list.delete(0, END)
            # 将用户好友依次添加到用户好友面板中
            for friend in self.find_user_friends_info_list:
                self.friend_list.insert(END, friend["name"] + "(" + friend["user_id"] + ")")
                online = "在线" if friend["online"] else "离线"
                self.friend_online_list.insert(END, online)

    def refuse_request(self, select_id, select_user_id):
        """
        拒绝添加好友菜单项点击事件
        :param select_id: 选中项id
        :param select_user_id: 选中的用户id
        :return:
        """
        # 发送请求
        response = self.create_thread(self.user_api.refuse_request, select_user_id)
        if response.text == SUCCESS:
            # 删除此请求项
            self.message_box.delete(select_id, select_id)
            # 从未读消息中删除此请求项
            if select_user_id in self.new_request_dict:
                self.new_request_dict.pop(select_user_id)
            # 从已读消息中删除此请求项
            if select_user_id in self.old_request_dict:
                self.old_request_dict.pop(select_user_id)

    def message_chat_box_click(self, event):
        """
        聊天面板窗口单击事件
        :param event: 事件参数
        :return:
        """
        # 创建菜单
        menu = Menu(self.message_chat_box, tearoff=0)
        # 添加菜单项
        menu.add_command(label="清空记录", command=lambda: self.clear_chat_record())
        # 将菜单面板放置在鼠标处
        menu.post(x=event.x_root, y=event.y_root)

    def clear_chat_record(self):
        """
        清空记录菜单项单击事件
        :return:
        """
        if 0 in self.current_message_focus_id:
            # 清空面板
            self.message_box.delete(2, END)
            # 清空已读信息
            self.old_message_info_list = []
        elif 1 in self.current_message_focus_id:
            # 清空面板
            self.message_box.delete(2, END)
            # 清空已读信息
            self.old_request_dict = {}
        else:
            # 设置面板为可以修改
            self.message_chat_box["state"] = NORMAL
            # 清空面板
            self.message_chat_box.delete("2.0", END)
            # 设置面板为禁止修改
            self.message_chat_box["state"] = DISABLED
            # 获取被单击的列表项
            select_item = self.friend_mes_list_box.get(self.current_message_focus_id)
            # 获取被单击的列表项用户id
            index_start = select_item.rfind("(")
            index_stop = select_item.rfind(")")
            select_user_id = select_item[index_start + 1:index_stop]
            # 清空已读信息
            if select_user_id in self.old_message_dict:
                self.old_message_dict[select_user_id] = []

    def entry_return(self, event):
        """
        在输入框插入换行
        :param event:
        :return:
        """
        pass

    def send_message(self, event):
        """
        发送信息
        :param event: 事件参数
        :return:
        """
        # 获取被单击的列表项用户id
        select_user_item = self.friend_mes_list_box.get(self.current_message_focus_id)
        index_start = select_user_item.rfind("(")
        index_stop = select_user_item.rfind(")")
        select_user_id = select_user_item[index_start + 1:index_stop]
        # 获取输入框内容
        message = self.mes_entry.get("1.0", END)[:-2]
        # 删除编辑框
        self.mes_entry.delete("1.0", END)
        # 发送请求
        response = self.create_thread(self.user_api.add_message, select_user_id, message)
        # 判断消息是否发送成功
        if response.text == SUCCESS:
            # 获取当前时间
            current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # 将时间字符串转化为时间对象
            current_date_time = datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
            # 封装数据
            message_dict = {
                'sender': self.user_id,
                'receiver': select_user_id,
                'message': message,
                'request': 0,
                'date_time': str(current_date_time)
            }
            # 将发送的消息添加到对应的已读消息中
            self.old_message_dict[select_user_id].append(message_dict)
            # 将消息显示到面板上
            self.insert_message(message_dict)

    def btn_friend_click(self):
        """
        好友按钮单击事件
        :return:
        """
        # 设置按钮被单击状态的图标
        self.set_image_type(1)

    def friend_list_click(self, event=None):
        """
        好友列表项单击事件
        :param event: 事件参数
        :return:
        """
        # 获取被单击的列表项id
        select_id = self.friend_list.curselection()
        self.friend_online_list.selection_clear(0, END)
        self.friend_online_list.selection_set(select_id)
        # 获取被单击的列表项内容
        select_user_item = self.friend_list.get(select_id)
        # 截取被单击的列表项用户id
        start_index = select_user_item.find("(")
        stop_index = select_user_item.find(")")
        select_user_id = select_user_item[start_index + 1:stop_index]
        # 在用户好友详细信息列表中寻找被双击列表项的详细信息
        for friend_info in self.find_user_friends_info_list:
            if select_user_id in friend_info.values():
                # 获取好友详细信息
                select_user_info = friend_info
                # 依次将用户详细信息更新到面板上
                for key in self.user_info_label_list:
                    # 判断是否是头像标签
                    if key == "image":
                        # 判断用户是否有头像，若无头像，则使用默认头像
                        if self.find_user_friends_image[select_user_id]:
                            self.user_info_label_list[key]["image"] = self.find_user_friends_image[select_user_id]
                        else:
                            self.user_info_label_list[key]["image"] = self.default_image
                    else:
                        if key == "online":
                            if select_user_info[key] == 1:
                                self.user_info_label_list[key]["text"] = "在线"
                            else:
                                self.user_info_label_list[key]["text"] = "离线"
                        else:
                            self.user_info_label_list[key]["text"] = select_user_info[key] if select_user_info[
                                key] else " "
                break

    def friend_online_list_click(self, event=None):
        """
        好友列表项单击事件
        :param event: 事件参数
        :return:
        """
        # 获取被单击的列表项id
        select_id = self.friend_online_list.curselection()
        self.friend_list.selection_clear(0, END)
        self.friend_list.selection_set(select_id)
        # 显示点击项的详细信息
        self.friend_list_click()

    def friend_list_double_click(self, event):
        """
        好友列表项双击事件
        :param event: 事件参数
        :return:
        """
        # 获取被单击的列表项id
        select_id = self.friend_list.curselection()
        self.friend_online_list.selection_clear(0, END)
        self.friend_online_list.selection_set(select_id)
        # 获取被单击的列表项用户id
        select_item = self.friend_list.get(select_id)
        # 截取被单击的列表项用户id
        start_index = select_item.find("(")
        stop_index = select_item.find(")")
        select_user_id = select_item[start_index + 1:stop_index]
        # 创建菜单
        menu = Menu(self.friend_list, tearoff=0)
        menu.add_command(label="发送信息", command=lambda: self.to_send_message(select_id, select_item, select_user_id))
        menu.add_separator()
        menu.add_command(label="删除好友", command=lambda: self.delete_user_friend(select_id, select_user_id))
        menu.add_separator()
        menu.add_command(label="查看详细信息", command=lambda: self.show_user_info(select_user_id))
        menu.add_separator()
        menu.add_command(label="刷新", command=lambda: self.get_info(select_id))
        # 将菜单面板放置在鼠标处
        menu.post(x=event.x_root, y=event.y_root)

    def friend_online_list_double_click(self, event=None):
        """
        好友列表项双击事件
        :param event: 事件参数
        :return:
        """
        # 获取被单击的列表项id
        select_id = self.friend_online_list.curselection()
        self.friend_list.selection_clear(0, END)
        self.friend_list.selection_set(select_id)
        # 显示点击项的详细信息
        self.friend_list_double_click(event)

    def to_send_message(self, select_id, select_item, select_user_id):
        """
        发送消息菜单项点击事件
        :param select_id: 选中项id
        :param select_item: 选中项内容
        :param select_user_id: 选中项用户id
        :return:
        """
        # 判断接受者是否是自己
        if self.user_id == select_user_id:
            return
        # 显示消息面板
        self.btn_mes_click()
        # 将当前用户添加到消息列表中
        self.user_message_set.add(select_user_id)
        # 获取消息列表
        mes_list = self.friend_mes_list_box.get(0, END)
        # 判断当前用户是否在消息列表中
        if select_item in mes_list:
            # 获取该用户所在位置
            index = mes_list.index(select_item)
            # 从当前消息列表中删除当前用户
            self.friend_mes_list_box.delete(index, index)
            self.friend_mes_num_list_box.delete(index, index)
        # 将此用户添加到消息列表中
        self.friend_mes_list_box.insert(2, select_item)
        self.friend_mes_num_list_box.insert(2, " ")
        # 默认激活该会话用户
        self.friend_mes_list_box.selection_clear(0, END)
        self.friend_mes_num_list_box.selection_clear(0, END)
        self.friend_mes_list_box.select_set(2)
        self.friend_mes_num_list_box.select_set(2)
        # 更新当前选中消息项id
        self.current_message_focus_id = (2,)
        # 将信息显示到面板上
        self.show_message_box(select_user_id)

    def delete_user_friend(self, select_id, select_user_id):
        """
        删除用户好友点击事件
        :param select_id: 选中的列表项id
        :param select_user_id: 选中的列表项用户id
        :return:
        """
        # 询问是否要删除当前用户
        result = tkinter.messagebox.askokcancel("请在三考虑", "你确定要删除当前用户嘛？")
        if result:
            if select_user_id == self.user_id:
                tkinter.messagebox.showinfo("错误", "你不能删除自己！")
                return
            # 删除好友
            response = self.user_api.delete_user_friend(select_user_id)
            if response.text == SUCCESS:
                # 从好友列表中删除此好友
                self.find_user_friends_set.remove(select_user_id)
                # 从好友列表面板中删除此好友
                self.friend_list.delete(select_id)
                self.friend_online_list.delete(select_id)
                # 删除后默认激活第一项
                self.friend_list.select_set(0)
                self.friend_online_list.select_set(0)
                tkinter.messagebox.showinfo("成功了", message="好友{}删除成功！".format(select_user_id))
            elif response.text == ERROR:
                tkinter.messagebox.showinfo("失败了", message="好友{}删除失败！".format(select_user_id))

    def show_user_info(self, select_user_id=None, user_info=None):
        """
        显示选中的列表项的详细信息
        :param select_user_id: 选中的列表项用户账号
        :param user_info: 选中的列表项用户个人信息
        :return:
        """
        if select_user_id:
            # 查询好友详细信息
            user_info = self.user_api.get_object(self.user_api.find_user_info(select_user_id).text)
        # 创建顶部面板
        top = self.init_top("详细信息", 500, 500)
        if user_info is None:
            return
        for index, key in enumerate(user_info):
            # 判断标签是否是图片
            if key == "image":
                # 判断用户是否有头像
                if user_info["image"]:
                    # 下载用户头像
                    file_path = self.user_api.download_image(user_info["image"], self.user_image_path)
                    # 创建默认图片对象
                    self.detail_image = self.get_image(file_path, (150, 150))
                else:
                    self.detail_image = self.default_image
                # 创建用户头像标签
                label = Label(top, image=self.detail_image)
                # 将用户头像显示在最顶部
                label.grid(row=0, column=0, columnspan=2, padx=500 / 2 - 200)
            else:
                # 创建用户信息标签
                Label(top, text=self.user_info_dict[key] + ":").grid(row=index + 1, column=0, sticky=E + N)
                if key == "online":
                    if user_info[key] == 1:
                        label = Label(top, text="在线")
                    else:
                        label = Label(top, text="离线")
                else:
                    label = Label(top, wraplength=200, justify='left', text=user_info[key])
                label.grid(row=index + 1, column=1, sticky=W)

    def btn_me_click(self):
        """
        我的列按钮单击事件
        :return:
        """
        # 设置按钮被单击状态的图标
        self.set_image_type(2)

    def btn_update_info(self):
        """
        修改信息按钮点击事件
        :return:
        """
        # 创建顶部面板
        top = self.init_top("修改个人信息", CHAT_WIDTH - 100, CHAT_HEIGHT - 100)
        # 获取用户信息
        user_info = self.user_api.get_object(self.user_api.find_user_info(self.user_id).text)
        user_info.pop("image")
        user_info.pop("online")
        # 用户信息编辑内容
        user_id_value = StringVar()
        name_value = StringVar()
        age_value = StringVar()
        # 创建放置信息的子面板
        user_info_box = Frame(top)
        user_info_box.place(x=(CHAT_WIDTH - 100) / 2, y=0, anchor=N)
        for index, key in enumerate(user_info):
            # 依次创建用户信息标签
            Label(user_info_box, text=self.user_info_dict[key] + ":").grid(row=index, column=0, sticky=E)
        # 创建用户信息编辑框
        # 账号
        Entry(user_info_box, textvariable=user_id_value, state=DISABLED).grid(row=0, column=1, sticky=W)
        # 设置默认值
        user_id_value.set(user_info["user_id"])
        # 昵称
        Entry(user_info_box, textvariable=name_value).grid(row=1, column=1, sticky=W)
        # 设置默认值
        name_value.set(user_info["name"])
        # 性别
        sex = ttk.Combobox(user_info_box, state='readonly')
        sex.grid(row=2, column=1, sticky=W)
        sex["value"] = ("男", "女", "其他", "保密")
        # 设置默认值
        if user_info["sex"] in sex["value"]:
            sex.set(user_info["sex"])
        # 年龄
        Label(user_info_box, textvariable=age_value, state=DISABLED).grid(row=3, column=1, sticky=W)
        # 生日
        # 获取当前时间
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month
        current_day = datetime.datetime.now().day
        # 放置日期的子控件
        date_frame = Frame(user_info_box)
        date_frame.grid(row=4, column=1, sticky=W)
        # 年
        year = ttk.Combobox(date_frame, width=4, state='readonly')
        year.grid(row=0, column=0)
        Label(date_frame, text="年").grid(row=0, column=1)
        year["value"] = tuple([current_year - i for i in range(current_year - 1970)])
        # 月
        month = ttk.Combobox(date_frame, width=2, state='readonly')
        month.grid(row=0, column=2)
        Label(date_frame, text="月").grid(row=0, column=3)
        month["value"] = tuple([i for i in range(1, 13)])
        # 日
        day = ttk.Combobox(date_frame, width=2, state='readonly')
        day.grid(row=0, column=4)
        Label(date_frame, text="日").grid(row=0, column=5)
        # 绑定年月切换事件
        year.bind("<<ComboboxSelected>>", lambda event: self.get_day(event, year, month, day, age_value))
        month.bind("<<ComboboxSelected>>", lambda event: self.get_day(event, year, month, day, age_value))
        day.bind("<<ComboboxSelected>>", lambda event: self.get_day(event, year, month, day, age_value))
        # 设置生日默认值
        if user_info["birthday"]:
            # 将年月日字符串分割为年,月,日
            date_list = user_info["birthday"].split("-")
            if len(date_list) == 3:
                year.set(int(date_list[0]))
                month.set(int(date_list[1]))
                day.set(int(date_list[2]))
            # 设置年龄默认值
            age_value.set(user_info["age"])
        # 简介
        info_text = Text(user_info_box, width=50, height=10, bd=1, relief="groove")
        info_text.grid(row=5, column=1)
        # 设置默认值
        if user_info["info"]:
            info_text.insert(END, user_info["info"])
        # 控件的内容列表
        value_list = {
            "name": name_value,
            "sex": sex,
            "age": age_value,
            "birthday": [year, month, day],
            "info": info_text
        }
        # 按钮
        btn_box = Frame(user_info_box)
        btn_box.grid(row=6, column=0, columnspan=2)
        Button(btn_box, text="提交",
               command=lambda: self.submit_update_info(top, user_info, value_list)).grid(row=0, column=0)
        Button(btn_box, text="取消", command=lambda: top.destroy()).grid(row=0, column=1)

    def submit_update_info(self, top, user_info, value_list):
        """
        修改信息面板提交按钮点击事件
        :param top: 顶部面板
        :param user_info: 用户个人信息
        :param value_list: 获取用户输入的信息的变量列表
        :return:
        """
        # 依次获取修改后的信息
        user_info["name"] = value_list["name"].get()
        user_info["sex"] = value_list["sex"].get()
        user_info["age"] = value_list["age"].get()
        # 依次获取年月日
        year = value_list["birthday"][0].get()
        month = value_list["birthday"][1].get()
        day = value_list["birthday"][2].get()
        user_info["birthday"] = year + "-" + month + "-" + day
        user_info["info"] = value_list["info"].get("0.0", END)
        # 提交修改信息
        response = self.create_thread(self.user_api.update_user_info, user_info)
        if response.text == SUCCESS:
            tkinter.messagebox.showinfo("成功了", message="用户信息修改成功！")
            # 销毁面板
            top.destroy()
        elif response.text == ERROR:
            tkinter.messagebox.showinfo("失败了", message="用户信息修改失败！")
        else:
            tkinter.messagebox.showinfo("出错了", message="出错了！")

    def btn_update_image(self):
        """
        修改头像按钮点击事件
        :return:
        """
        # 创建顶部面板
        top = self.init_top("修改头像", 200, 200)
        # 创建用户头像图片对象
        photo = self.find_user_friends_image[self.user_id] if self.user_id in self.find_user_friends_image else None
        # 创建用户头像标签
        label = Label(top, image=photo)
        label.pack()
        # 选择头像图片文件按钮
        Button(top, text="上传头像", command=lambda: self.choose_image_to_upload(label)).pack()
        # 确认上传按钮
        Button(top, text="确认", command=lambda: self.submit_upload_image(top)).pack()

    def choose_image_to_upload(self, label):
        """
        选择要上传的头像图片
        :return:
        """
        # 仅支持上传jpg,png类型的文件
        file_types = [('jpg', '*.jpg'), ('png', '*.png')]
        # 选择要上传jpg,png文件
        file_path = filedialog.askopenfilename(title='上传照片', filetypes=file_types)
        # 判断有是否选择文件
        if file_path:
            # 创建选取的用户头像图片对象
            self.choose_image = self.get_image(file_path, (150, 150))
            # 将选取的用户头像图片更新到面板上
            label["image"] = self.choose_image
            # 用户选取的头像图片路径
            self.choose_image_path = file_path

    def submit_upload_image(self, top):
        """
        上传用户头像文件
        :param top: 顶部面板
        :return:
        """
        # 判断用户是否选择头像图片文件
        if self.choose_image_path:
            # 上传用户头像
            response = self.create_thread(self.user_api.upload_image, self.choose_image_path)
            if response.text == SUCCESS:
                tkinter.messagebox.showinfo("成功了", message="头像修改成功！")
                # 更新用户选择的头像
                self.find_user_friends_image[self.user_id] = self.choose_image
                # 销毁顶部面板
                top.destroy()
            elif response.text == ERROR:
                tkinter.messagebox.showinfo("失败了", message="头像修改失败！")
            else:
                tkinter.messagebox.showinfo("出错了", message="出错了！")

    def btn_update_password(self):
        """
        更新密码按钮点击事件
        :return:
        """
        # 创建顶部面板
        top = self.init_top("修改密码", 200, 100)
        # 存放密码变量
        password_value = StringVar()
        # 密码标签
        Label(top, text="原密码：").grid(row=0, column=0, sticky=E)
        # 密码输入框
        password_entry = Entry(top, width=10, textvariable=password_value, show="*")
        password_entry.grid(row=0, column=1, sticky=W)
        # 绑定回车事件
        password_entry.bind("<Return>", lambda event: self.confirm_password(top, password_value, event))
        btn_frame = Frame(top)
        btn_frame.grid(row=1, column=0, columnspan=2)
        # 下一步按钮
        Button(btn_frame, text="下一步", command=lambda: self.confirm_password(top, password_value)).pack()

    def confirm_password(self, top, password_value, event=None):
        """
        判断原密码是否输入正确
        :param top: 顶部面板
        :param password_value:存放密码的变量
        :param event: 事件参数
        :return:
        """
        # 判断原密码是否输入正确
        if password_value.get() == self.password:
            # 销毁原控件
            for child in top.winfo_children():
                child.destroy()
            password_value.set("")
            # 存放确认密码变量
            confirm_password_value = StringVar()
            # 新密码标签
            Label(top, text="新密码：").grid(row=0, column=0, sticky=E)
            # 新密码输入框
            password_entry = Entry(top, width=10, textvariable=password_value, show="*")
            password_entry.grid(row=0, column=1, sticky=W)
            # 确认密码标签
            Label(top, text="确认密码：").grid(row=1, column=0, sticky=E)
            # 确认密码输入框
            confirm_password_entry = Entry(top, width=10, textvariable=confirm_password_value, show="*")
            confirm_password_entry.grid(row=1, column=1, sticky=W)
            # 绑定回车事件
            confirm_password_entry.bind("<Return>",
                                        lambda event: self.submit_update_password(top, password_value,
                                                                                  confirm_password_value, event))
            btn_frame = Frame(top)
            btn_frame.grid(row=2, column=0, columnspan=2)
            # 提交按钮
            Button(btn_frame, text="提交",
                   command=lambda: self.submit_update_password(top, password_value, confirm_password_value)).pack()
        else:
            tkinter.messagebox.showinfo("失败了", message="原密码输入错误！")

    def submit_update_password(self, top, password_value, confirm_password_value, event=None):
        """
        修改密码提交按钮事件
        :param top: 顶部面板
        :param password_value: 存放密码的变量
        :param confirm_password_value: 存放确认密码的变量
        :param event: 事件参数
        :return:
        """
        # 判断两次密码输入是否一致
        if password_value.get() == confirm_password_value.get():
            # 提交修改信息
            response = self.create_thread(self.user_api.update_password, password_value.get())
            if response.text == SUCCESS:
                tkinter.messagebox.showinfo("成功了", message="密码修改成功！")
                # 销毁顶部面板
                top.destroy()
            elif response.text == ERROR:
                tkinter.messagebox.showinfo("失败了", message="失败了！")
        else:
            tkinter.messagebox.showinfo("失败了", message="两次密码输入不一致！")

    def btn_add_friend(self):
        """
        添加好友按钮点击事件
        :return:
        """
        # 创建顶部面板
        top = self.init_top("添加好友", 400, 400)
        # 存放查找的用户账号
        find_user_id = StringVar()
        # 存放复选框的变量
        find_online = IntVar()
        # 默认不选中
        find_online.set(0)
        # 用户编辑框子面板
        edit_box = Frame(top)
        edit_box.pack()
        # 查找结果列表
        result_list = Listbox(top, bd=0)
        result_list.pack(fill="both", expand=1)
        # 绑定双击事件
        # result_list.bind("<Double-Button-1>", lambda event: self.find_user_info_double_click(top, result_list, event))
        result_list.bind("<Button-3>", lambda event: self.find_user_info_double_click(top, result_list, event))
        # 字符串格式化对齐
        text = self.format_text("账号", "昵称", "简介")
        result_list.insert(END, text)
        # 查找用户账号输入框
        entry_find_user = Entry(edit_box, textvariable=find_user_id)
        entry_find_user.grid(row=0, column=0)
        # 绑定回车事件
        entry_find_user.bind("<Return>",
                             lambda event: self.submit_find_user_info(find_user_id, result_list,
                                                                      event))
        # 确认的复选框按钮
        Checkbutton(edit_box, text="仅看在线", variable=find_online, onvalue=1, offvalue=0).grid(row=1, column=0, sticky=W)
        # 查找按钮
        Button(edit_box, text="查找好友",
               command=lambda: self.submit_find_user_info(find_user_id, result_list)).grid(row=0, column=1)
        Button(edit_box, text="查找所有",
               command=lambda: self.submit_find_all_user_info(find_online, result_list)).grid(row=1, column=1)

    def submit_find_user_info(self, find_user_id, result_list, event=None):
        """
        查找用户按钮点击事件
        :param find_user_id: 查找的用户账号
        :param result_list: 显示查找结果的控件
        :param event: 事件参数
        :return:
        """
        # 清空面板
        result_list.delete(1, END)
        # 判断输入框是否为空
        if find_user_id.get():
            # 查找用户信息
            response = self.create_thread(self.user_api.find_user_info, find_user_id.get())
            find_user_info = self.user_api.get_object(response.text)
            # 判断是否查询到信息
            if find_user_info:
                user_id = find_user_info["user_id"] if find_user_info["user_id"] else ""
                name = find_user_info["name"] if find_user_info["name"] else ""
                info = find_user_info["info"] if find_user_info["info"] else ""
                # 字符串格式化对齐
                text = self.format_text(user_id, name, info)
            else:
                text = "{0:^60}".format("查找不到此用户")
            # 将信息插入到面板尾部
            result_list.insert(END, text)

    def submit_find_all_user_info(self, find_online, result_list):
        """
        查找所有用户按钮点击事件
        :param find_online: 是否仅查询在线用户
        :param result_list: 显示查找结果的控件
        :return:
        """
        # 清空面板
        result_list.delete(1, END)
        # 判断是否仅查找在线用户
        if find_online.get():
            # 仅查找在线用户
            find_all_user_info = self.user_api.get_object(self.user_api.find_user_online_info().text)
        else:
            # 查找所有用户
            find_all_user_info = self.user_api.get_object(self.user_api.find_all_user_info().text)
        # 依次将用户信息显示到面板上
        for find_user_info in find_all_user_info:
            # 判断是否查询到信息
            if find_user_info:
                user_id = find_user_info["user_id"] if find_user_info["user_id"] else ""
                name = find_user_info["name"] if find_user_info["name"] else ""
                info = find_user_info["info"] if find_user_info["info"] else ""
                # 字符串格式化对齐
                text = self.format_text(user_id, name, info)
                # 将信息插入到面板尾部
                result_list.insert(END, text)

    def find_user_info_double_click(self, top, result_list, event):
        """
        查找结果列表项双击事件
        :param top: 顶部面板
        :param result_list: 显示查找结果的控件
        :param event: 事件参数
        :return:
        """
        # 获取被单击的列表项id
        select_id = result_list.curselection()
        if 0 in select_id:
            return
        try:
            # 获取被单击的列表项内容
            select_user_item = result_list.get(select_id)
            # 去除两侧空格
            select_user_item = select_user_item.lstrip()
            select_user_item = select_user_item.rstrip()
            # 截取用户id和昵称的开始和结束下标
            end = select_user_item.find(chr(12288))
            start = select_user_item.rfind(chr(12288))
            # 获取被单击的列表项用户id和昵称
            select_user_id = select_user_item[:end]
            select_user_name = select_user_item[start + 1:]
            # 创建菜单
            menu = Menu(top, tearoff=0)
            if select_user_id in self.find_user_friends_set:
                # 创建子按钮
                menu.add_command(label="发送信息",
                                 command=lambda: self.to_send_message(select_id, select_user_name, select_user_id))
            else:
                # 创建子按钮
                menu.add_command(label="添加好友", command=lambda: self.add_request(select_user_id))
            menu.add_separator()
            menu.add_command(label="查看详细信息", command=lambda: self.show_user_info(select_user_id))
            menu.add_separator()
            # 将菜单面板放置在鼠标处
            menu.post(x=event.x_root, y=event.y_root)
        except Exception as e:
            print("请选择被点击项:{}".format(e))

    def add_request(self, select_user_id):
        """
        添加好友菜单点击事件
        :param select_user_id: 选中的列表项
        :return:
        """
        # 发送请求
        response = self.create_thread(self.user_api.add_request, select_user_id)
        if response.text == SUCCESS:
            tkinter.messagebox.showinfo("成功了", message="添加好友请求发送成功！")
        elif response.text == ERROR:
            tkinter.messagebox.showinfo("失败了", message="添加好友请求发送失败！")

    def btn_logout_user(self):
        """
        退出当前用户登录
        :return:
        """
        # 询问是否要退出登录
        result = tkinter.messagebox.askokcancel("退出登录", "你真的要退出嘛？")
        if result:
            # 退出当前用户登录
            self.__del__()

    def btn_delete_user(self):
        """
        删除当前用户
        :return:
        """
        # 询问是否要删除当前用户
        result = tkinter.messagebox.askokcancel("请在三考虑", "你确定要删除当前用户嘛？")
        if result:
            # 创建顶部面板
            top = self.init_top("请在三考虑", 200, 100)
            text = "若要删除当前用户，您则失去所有信息，包括个人信息，好友，聊天记录等....."
            Label(top, wraplength=200, justify='left', text=text).pack()
            # 存放复选框的变量
            confirm = IntVar()
            # 默认不选中
            confirm.set(0)
            # 确认的复选框按钮
            Checkbutton(top, text="我已阅读", variable=confirm, onvalue=1, offvalue=0).pack(anchor=W)
            # 提交按钮
            Button(top, text="确定", command=lambda: self.submit_delete_user(confirm)).pack()

    def submit_delete_user(self, confirm):
        """
        点击确定删除用户按钮
        :param confirm: 是否已读删除警告内容
        :return:
        """
        if confirm.get():
            # 提交修改信息
            response = self.create_thread(self.user_api.user_delete)
            if response.text == SUCCESS:
                tkinter.messagebox.showinfo("成功了", message="用户删除成功！")
                # 退出程序
                self.__del__()
            elif response.text == ERROR:
                tkinter.messagebox.showinfo("失败了", message="用户删除失败！")

    def create_thread(self, func, *args):
        """
        创建并启动多线程
        :param func: 函数名
        :param args: 函数所需参数
        :return:
        """
        # 创建多线程
        init_thread = MyThread(func, *args)
        # 启动多线程
        init_thread.start()
        if func != self.user_api.user_socket:
            init_thread.join()
        return init_thread.get_result()

    def __del__(self):
        """
        点击关闭按钮时，退出当前用户登录
        :return:
        """
        # 退出当前用户登录
        self.create_thread(self.user_api.user_logout)
        # 关闭socket连接
        self.user_api.ws.close()
        # 关闭session连接
        self.user_api.my_session.close()
        # 销毁面板
        self.root.destroy()
        # 将用户消息信息保存到本地
        with open(CACHE_FILE_PATH + "/chat_record.pkl", "wb") as file:
            # 封装数据
            chat_record = {
                # 已读信息
                "old_message_info_list": self.old_message_info_list,
                "old_request_dict": self.old_request_dict,
                "old_message_dict": self.old_message_dict
            }
            # 将聊天记录保存到本地文件中
            pickle.dump(chat_record, file)
        # 退出程序
        os._exit(0)
