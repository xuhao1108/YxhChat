import pickle
import os
import tkinter.messagebox
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk

from Client.User.my_thread import MyThread
from Client.User.user_api import UserApi
from Client.Pane.login_after import After
from Client.settings import LOGIN_TITLE, LOGIN_WIDTH, LOGIN_HEIGHT, HIDE_HEIGHT, REGISTER_WIDTH, REGISTER_HEIGHT
from Client.settings import USER_EXIST, USER_NOT_EXIST, NOT_CORRECT, SUCCESS, ERROR, ONLINE
from Client.settings import CACHE_FILE_PATH


class Before(object):
    """
    用户登录前的面板
    """

    def __init__(self):
        """
        登录窗口面板初始化
        """
        # 创建面板对象
        self.root = Tk()

        # 创建api连接对象
        self.user_api = UserApi()

        # 账号输入框下拉控件
        self.entry_user_id = None
        # 用来存放账号的变量
        self.user_id = StringVar()
        # 用来存放密码的变量
        self.password = StringVar()
        # 用来存放确认密码的变量
        self.confirm_password = StringVar()
        # 用来存放按钮菜单是否被点击
        self.menu_button = False
        # 用来存放密码的变量
        self.remember_password = IntVar()
        # 默认为记住密码
        self.remember_password.set(1)
        # 用来存放自动登录的变量
        self.auto_login = IntVar()
        # 默认图片对象，若图片不能正常显示，则显示默认图片对象
        self.default_image = self.get_image(CACHE_FILE_PATH + '/image/image.png', (150, 150))

        # 初始化主面板
        self.init_root()
        # 初始化输入框及登录按钮
        self.init_entry()
        # 初始化隐藏面板
        self.init_hidden_menu()

        # 用于存放所有用户信息的字典
        self.user_info_dict = dict()
        # 读取本地文件,并显示在输入框中
        self.read_user_info()

        # 进入消息循环
        self.root.mainloop()

    def init_root(self):
        """
        根面板初始化
        :return:
        """
        # 设置面板标题
        self.root.title(LOGIN_TITLE)
        # 计算屏幕中心位置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_width = (screen_width - LOGIN_WIDTH) / 2
        center_height = (screen_height - LOGIN_HEIGHT) / 2
        root_size = "%dx%d+%d+%d" % (LOGIN_WIDTH, LOGIN_HEIGHT, center_width, center_height)
        # 设置面板大小,并居屏幕中心
        self.root.geometry(root_size)
        # 禁止用户改变面板大小
        self.root.resizable(0, 0)

    def init_entry(self):
        """
        输入框控件初始化
        :return:
        """
        # 显示图片
        Label(self.root, image=self.default_image).pack()
        # 创建子框架存放账号密码控件
        frame = Frame(self.root)
        frame.pack()
        # 账号标签
        Label(frame, text="账号：").grid(row=0, column=0)
        # 账号输入框列表
        self.entry_user_id = ttk.Combobox(frame, textvariable=self.user_id)
        self.entry_user_id.grid(row=0, column=1)
        # 账号输入框绑定切换选择事件
        self.entry_user_id.bind("<<ComboboxSelected>>", self.combobox_selected)
        # 账号输入框绑定键盘回车键事件
        self.entry_user_id.bind("<Return>", self.btn_login_click)
        # 账号输入框绑定键盘退格键事件
        self.entry_user_id.bind("<BackSpace>", self.combobox_clear)
        # 删除此账号密码的按钮
        Button(frame, text="x", command=self.delete_user).grid(row=0, column=2, padx=3)
        # 密码标签
        Label(frame, text="密码：").grid(row=1, column=0, pady=5)
        # 密码输入框
        entry_password = Entry(frame, textvariable=self.password, width=21, show="*")
        entry_password.grid(row=1, column=1, pady=5)
        # 密码输入框绑定键盘回车事件
        entry_password.bind("<Return>", self.btn_login_click)
        # 登录按钮
        btn_login = Button(self.root, width=10, height=2, text="登录", command=self.btn_login_click)
        btn_login.pack(pady=15)

    def init_hidden_menu(self):
        """
        隐藏菜单初始化
        :return:
        """
        # 按钮菜单
        Button(self.root, width=4, text="v", command=self.menu_button_click).place(x=LOGIN_WIDTH / 2,
                                                                                   y=LOGIN_HEIGHT,
                                                                                   anchor="s")
        # 隐藏面板
        hide_frame = Frame(self.root, width=LOGIN_WIDTH, height=HIDE_HEIGHT)
        hide_frame.place(x=0, y=LOGIN_HEIGHT)
        # 记住密码选项
        Checkbutton(hide_frame, text="记住密码", variable=self.remember_password, onvalue=1, offvalue=0).grid(
            row=0, column=0, padx=25, pady=15)
        # 自动登录选项
        Checkbutton(hide_frame, text="自动登录", variable=self.auto_login, onvalue=1, offvalue=0).grid(
            row=1, column=0, padx=25, pady=15)
        # 注册按钮
        Button(hide_frame, width=10, height=2, text="注册", command=self.btn_register_click).grid(row=0, column=1)
        # 忘记密码按钮
        Button(hide_frame, width=10, height=2, text="忘记密码", command=self.btn_ignore_password_click).grid(row=1,
                                                                                                         column=1)

    def read_user_info(self):
        """
        读取本地存储的用户账号和密码
        :return:
        """
        # 判断是否存在账号密码的信息
        try:
            # 若不存在则会抛出异常
            with open(CACHE_FILE_PATH + "/user_info.pkl", "rb") as file:
                # 获取账号信息
                self.user_info_dict = pickle.load(file)
                # 存放用户账号的列表
                user_id_list = list()
                # 依次取出用户账号
                for user_id in self.user_info_dict:
                    # 将账号添加到列表中
                    user_id_list.append(user_id)
                # 将用户账号列表添加到账号输入框列表中
                self.entry_user_id["value"] = (tuple(user_id_list))
                # 默认选择第一项
                self.entry_user_id.current(0)
                # 关联默认选择用户密码
                self.password.set(self.user_info_dict[self.entry_user_id.get()])
        except Exception as e:
            print("文件user_info.pkl不存在:{}".format(e))

    def write_user_info(self):
        """
        将用户账号密码保存到本地
        :return:
        """
        # 将用户信息保存到本地文件中
        with open(CACHE_FILE_PATH + "/user_info.pkl", "wb") as file:
            # 判断是否保存密码
            if self.remember_password.get():
                self.user_info_dict[self.user_id.get()] = self.password.get()
            else:
                self.user_info_dict[self.user_id.get()] = ""
            # 将用户信息保存到本地文件中
            pickle.dump(self.user_info_dict, file)

    def get_image(self, file_path, size):
        """
        获取图片对象
        :param file_path:图片路径
        :param size:图片缩放尺寸
        :return:
        """
        if os.path.isfile(file_path):
            # 打开图片
            image = Image.open(file_path)
            # 将图片缩放为150*150
            image.thumbnail(size)
            # 创建图片按钮对象
            photo = ImageTk.PhotoImage(image)
            return photo

    def combobox_clear(self, event=None):
        """
        账号输入框绑定退格键事件
        :param event:事件参数
        :return:
        """
        # 将账号输入框清空
        # self.user_id.set("")
        # 将密码输入框清空
        self.password.set("")

    def combobox_selected(self, event=None):
        """
        账号输入框绑定切换选择事件
        :param event: 事件参数
        :return:
        """
        # 将账号输入框和密码输入框关联
        self.password.set(self.user_info_dict[self.user_id.get()])

    def delete_user(self):
        """
        删除当前输入框的用户
        :return:
        """
        # 判断要删除的用户是否存储在本地的用户信息字典中
        if self.user_id.get() in self.user_info_dict:
            # 删除此用户
            self.user_info_dict.pop(self.user_id.get())
            # 更新用户下拉列表
            self.entry_user_id["value"] = (tuple(self.user_info_dict.keys()))
            # 判断下拉列表是否还有用户
            if len(self.entry_user_id["value"]) > 1:
                # 默认选择第一项
                self.entry_user_id.current(0)
                # 关联默认选择用户密码
                self.password.set(self.user_info_dict[self.entry_user_id.get()])
        else:
            # 将输入框清空
            self.user_id.set("")
            self.password.set("")

    def btn_login_click(self, event=None):
        """
        登录按钮点击事件
        :param event: 事件参数
        :return:
        """
        # 判断账号密码输入框是否为空
        if len(self.user_id.get()) == 0 and len(self.password.get()) == 0:
            tkinter.messagebox.showinfo("出错了", message="账号和密码不能为空！")
        elif len(self.user_id.get()) == 0:
            tkinter.messagebox.showinfo("出错了", message="账号不能为空！")
        elif len(self.password.get()) == 0:
            tkinter.messagebox.showinfo("出错了", message="密码不能为空！")
        else:
            # 发送请求，并获取请求结果
            response = self.create_thread(self.user_api.user_login, self.user_id.get(), self.password.get())
            # 判断请求结果
            if response == SUCCESS:
                tkinter.messagebox.showinfo("成功了", message="登录成功！")
                # 登录成功
                self.login_success()
            elif response == NOT_CORRECT:
                tkinter.messagebox.showinfo("失败了", message="账号或密码不正确，请重新输入！")
                # 将密码输入框清空
                self.password.set("")
            elif response == ONLINE:
                tkinter.messagebox.showinfo("失败了", message="用户已登录！")
            elif response == ERROR:
                tkinter.messagebox.showinfo("失败了", message="登录失败，请重试！")
            elif response == USER_NOT_EXIST:
                # 输入的用户不存在，询问是否要注册用户
                result = tkinter.messagebox.askyesno("出错了", message="用户不存在，是否去注册用户！")
                if result:
                    # 打开注册用户面板
                    self.btn_register_click()

    def login_success(self):
        """
        登录成功后的操作
        :return:
        """
        # 销毁主面板
        self.root.destroy()
        # 将用户账号密码保存到本地
        self.write_user_info()
        # 创建登录成功面板
        After(self.user_id.get(), self.password.get(), self.user_api)

    def menu_button_click(self):
        """
        隐藏面板按钮点击事件
        :return:
        """
        # 判断隐藏面板是否展开
        if self.menu_button:
            # 设置面板大小
            self.root.geometry(str(LOGIN_WIDTH) + "x" + str(LOGIN_HEIGHT))
            # 更新面板展开标记
            self.menu_button = False
        else:
            # 设置面板大小
            self.root.geometry(str(LOGIN_WIDTH) + "x" + str(LOGIN_HEIGHT + 100))
            # 更新面板展开标记
            self.menu_button = True

    def btn_register_click(self):
        """
        首页注册按钮点击事件
        :return:
        """
        # 创建顶部面板
        top = Toplevel(self.root)
        # 设置顶部面板标题
        top.title("用户注册")
        # 计算顶部面板居中位置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_width = (screen_width - REGISTER_WIDTH) / 2
        center_height = (screen_height - REGISTER_HEIGHT) / 2
        root_size = "%dx%d+%d+%d" % (REGISTER_WIDTH, REGISTER_HEIGHT, center_width, center_height)
        # 设置顶部面板大小并居中
        top.geometry(root_size)
        # 账号标签
        Label(top, text="账号：").grid(row=0, column=0, sticky=E)
        # 账号输入框
        Entry(top, textvariable=self.user_id).grid(row=0, column=1)
        # 密码标签
        Label(top, text="密码：").grid(row=1, column=0, pady=5, sticky=E)
        # 密码输入框
        entry_password = Entry(top, textvariable=self.password, show="*")
        entry_password.grid(row=1, column=1, pady=5)
        # 确认密码标签
        Label(top, text="确认密码：").grid(row=2, column=0, pady=5, sticky=E)
        # 密码输入框
        entry_password = Entry(top, textvariable=self.confirm_password, show="*")
        entry_password.grid(row=2, column=1, pady=5)
        # 密码输入框绑定键盘回车事件
        entry_password.bind("<Return>", lambda event: self.btn_register_user_click(top, event))
        frame = Frame(top)
        frame.grid(row=3, column=0, columnspan=2)
        # 注册用户按钮
        Button(frame, width=10, height=2, text="注册", command=lambda: self.btn_register_user_click(top)).grid(row=0,
                                                                                                             column=0,
                                                                                                             padx=40)
        # 取消按钮
        Button(frame, width=10, height=2, text="取消", command=lambda: top.destroy()).grid(row=0, column=1)

    def btn_ignore_password_click(self):
        """
        忘记密码按钮单击事件
        :return:
        """
        tkinter.messagebox.showinfo("？？？", message="那我也没办法咯！")

    def btn_register_user_click(self, top, event=None):
        """
        注册用户事件
        :param top:顶部面板
        :param event:事件参数
        :return:
        """
        # 判断输入框是否为空
        if len(self.user_id.get()) == 0 and len(self.password.get()) == 0 and len(self.confirm_password.get()):
            tkinter.messagebox.showinfo("出错了", message="账号、密码和确认密码不能为空！")
        elif len(self.user_id.get()) == 0:
            tkinter.messagebox.showinfo("出错了", message="账号不能为空！")
        elif len(self.password.get()) == 0:
            tkinter.messagebox.showinfo("出错了", message="密码不能为空！")
        elif len(self.confirm_password.get()) == 0:
            tkinter.messagebox.showinfo("出错了", message="确认密码不能为空！")
        else:
            # 判断密码和确认密码是否相同
            if self.password.get() != self.confirm_password.get():
                tkinter.messagebox.showinfo("出错了", message="密码和确认密码不相同！")
            else:
                # 发送请求，并获取请求结果
                response = self.create_thread(self.user_api.user_register, self.user_id.get(), self.password.get())
                # 判断请求结果
                if response.text == SUCCESS:
                    tkinter.messagebox.showinfo("成功啦！", message="注册成功，赶快去登录吧！")
                    # 销毁顶部面板
                    top.destroy()
                elif response.text == ERROR:
                    tkinter.messagebox.showinfo("失败了", message="注册失败，请重试！")
                elif response.text == USER_EXIST:
                    tkinter.messagebox.showinfo("出错了", message="用户已存在，请重新注册！")

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
        init_thread.join()
        return init_thread.get_result()

    def __del__(self):
        """
        程序退出时，将用户账号密码保存到本地
        :return:
        """
        # 将用户账号密码保存到本地
        self.write_user_info()
