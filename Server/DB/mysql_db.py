import os
import pymysql

from Server.User.user_info import User
from Server.log import logger
from Server.settings import BASE_URL
from Server.settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from Server.settings import SUCCESS, ERROR, USER_EXIST, USER_NOT_EXIST, IS_FRIEND, NOT_FRIEND, SEND_MESSAGE, \
    SEND_REQUEST, AGREE_REQUEST, REFUSE_REQUEST


class MySQLDb(object):
    """
    连接数据库
    """

    def __init__(self):
        """
        连接数据库
        """
        # 创建数据库连接对象
        self.connect = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB)
        # 创建数据库游标对象
        self.cursor = self.connect.cursor(cursor=pymysql.cursors.DictCursor)

    def __del__(self):
        """
        关闭数据库
        :return:
        """
        # 关闭数据库游标对象
        self.cursor.close()
        # 关闭数据库连接对象
        self.connect.close()

    def find_table_info(self, database):
        """
        查看表信息
        :param database:
        :return:
        """
        try:
            # 查看所有表
            self.cursor.execute("show tables;")
            # 获取查询结果
            db_list = self.cursor.fetchall()
            # 判断要找的表是否存在
            for db in db_list:
                for key in db:
                    if database in db[key]:
                        # 查看表的sql语句
                        admin_find_sql = "SELECT * FROM {};".format(database)
                        # 执行sql语句
                        self.cursor.execute(admin_find_sql)
                        # 获取表信息
                        admin_find_result = self.cursor.fetchall()
                        # 返回表信息
                        return admin_find_result
        except Exception as e:
            logger.exception("查看表{}信息失败！原因：{}".format(database, e))


class CreateDb(MySQLDb):
    """
    创建表和触发器
    """

    def __init__(self):
        """
        判断是否存在表和触发器
        """
        # 调用父类构造方法
        super().__init__()
        # 判断数据库中是否有表
        # table_exist = self.cursor.execute("SHOW TABLES;")
        # if not table_exist:
        #     # 创建表信息
        #     self._create_tables()
        # # 判断数据库中是否有触发器
        trigger_exist = self.cursor.execute("SHOW TRIGGERS;")
        if not trigger_exist:
            # 创建触发器
            self._create_trigger()

    def _create_tables(self):
        """
        创建表:user,user_friends,user_info,"SEND_MESSAGE"
        :return:
        """
        try:
            with open(os.path.dirname(__file__) + "/SQL/chat.sql", "r") as f:
                # 获取创建表的sql语句
                table_sql = f.read()
                # 执行sql语句
                self.cursor.execute(table_sql)
                logger.info("表创建成功！")
        except Exception as e:
            self.connect.rollback()
            logger.exception("表创建失败！原因:{}".format(e))
        finally:
            # 提交执行操作
            self.connect.commit()

    def _create_trigger(self):
        """
        创建触发器:自动在user_info,user_friends表中添加user信息
        :return:
        """
        try:
            with open(os.path.dirname(__file__) + "/SQL/chat_trigger.sql", "r") as f:
                # 获取创建触发器的sql语句
                trigger_sql = f.read()
                # 执行sql语句
                self.cursor.execute(trigger_sql)
                logger.info("触发器创建成功！")
        except Exception as e:
            self.connect.rollback()
            logger.exception("触发器创建失败！原因:{}".format(e))
        finally:
            # 提交执行操作
            self.connect.commit()


class DbUser(CreateDb):
    """
    对user表进行增删改查的操作
    """

    def add_user(self, user):
        """
        添加用户
        :param user:
        :return:
        """
        # 判断用户是否存在
        if not self.find_user(user):
            try:
                # 添加用户的sql语句
                add_user_sql = "INSERT INTO user(user_id,password) VALUES(%s,%s);"
                # 要添加的用户信息
                params = [user.user_id, user.password]
                # 执行sql语句
                self.cursor.execute(add_user_sql, params)
                logger.info("用户{}注册成功！".format(user.user_id))
                return SUCCESS
            except Exception as e:
                self.connect.rollback()
                logger.exception("用户{}注册失败！原因：{}".format(user.user_id, e))
                return ERROR
            finally:
                # 提交执行操作
                self.connect.commit()
        else:
            return USER_EXIST

    def delete_user(self, user):
        """
        删除用户
        :return:
        """
        # 判断用户是否存在
        if self.find_user(user):
            try:
                # 删除用户的sql语句
                add_sql = "DELETE FROM user WHERE user_id=%s;"
                # 要删除的用户账号
                params = [user.user_id]
                # 执行sql语句
                self.cursor.execute(add_sql, params)
                logger.info("用户{}注销成功！".format(user.user_id))
                return SUCCESS
            except Exception as e:
                self.connect.rollback()
                logger.exception("用户{}注销失败！原因：{}".format(user.user_id, e))
                return ERROR
            finally:
                # 提交执行操作
                self.connect.commit()
        else:
            return USER_NOT_EXIST

    def update_password(self, user):
        """
        修改用户密码
        :param user:
        :return:
        """
        # 判断用户是否存在
        if self.find_user(user):
            try:
                # 修改用户密码的sql语句
                update_password_sql = "UPDATE user SET password=%s where user_id=%s;"
                # 要修改的用户账号和密码
                params = [user.password, user.user_id]
                # 执行sql语句
                self.cursor.execute(update_password_sql, params)
                logger.info("用户{}密码修改成功！新密码:{}".format(user.user_id, user.password))
                return SUCCESS
            except Exception as e:
                self.connect.rollback()
                logger.exception("用户{}密码修改失败！原因：{}".format(user.user_id, e))
                return ERROR
            finally:
                # 提交执行操作
                self.connect.commit()
        else:
            return USER_NOT_EXIST

    def find_user(self, user):
        """
        查找一个用户
        :param user:
        :return:
        """
        try:
            # 查找一个用户的sql语句
            find_user_sql = "SELECT * FROM user WHERE user_id=%s;"
            # 要查找一个用户的账号
            params = [user.user_id]
            # 执行sql语句
            self.cursor.execute(find_user_sql, params)
            # 获取查询结果
            find_user_result = self.cursor.fetchone()
            # 返回查询结果
            return find_user_result
        except Exception as e:
            logger.exception(e)


class DbUserFriends(DbUser):
    """
    对user_friends表进行改查的操作
    """

    def add_user_friend(self, user, friend):
        """
        添加用户好友
        :param user:
        :param friend:
        :return:
        """
        # 判断用户和好友是否存在
        if self.find_user(user) and self.find_user(friend):
            try:
                # 获取用户好友列表
                friend_set = self.find_user_friends(user)
                # 判断好友是否在用户好友列表中
                if friend.user_id not in friend_set:
                    # 将好友添加到好友列表中
                    friend_set.add(friend.user_id)
                    # 将用户好友集合转化为字符串
                    friend_str = ",".join(friend_set)
                    # 要更新的用户好友sql语句
                    add_friend_sql = "UPDATE user_friends SET friends=%s WHERE user_id=%s;"
                    # 更新的用户好友列表
                    params = [friend_str, user.user_id]
                    # 执行sql语句
                    self.cursor.execute(add_friend_sql, params)
                    logger.info("用户{}添加好友{}成功！".format(user.user_id, friend.user_id))
                    return SUCCESS
                else:
                    return IS_FRIEND
            except Exception as e:
                self.connect.rollback()
                logger.exception("用户{}添加好友{}失败！原因：{}".format(user.user_id, friend.user_id, e))
                return ERROR
            finally:
                # 提交执行操作
                self.connect.commit()
        else:
            return USER_NOT_EXIST

    def delete_user_friend(self, user, friend):
        """
        删除用户好友
        :param user:
        :param friend:
        :return:
        """
        # 判断用户和好友是否存在
        if self.find_user(user) and self.find_user(friend):
            try:
                # 获取用户好友列表
                friend_set = self.find_user_friends(user)
                # 判断用户好友列表是否为空或者好友是否在用户好友列表中
                if friend.user_id in friend_set:
                    # 将好友从用户好友列表中删除
                    friend_set.remove(friend.user_id)
                    # 将用户好友集合转化为字符串
                    friend_str = ",".join(friend_set)
                    # 删除好友的sql语句
                    delete_friend_sql = "UPDATE user_friends SET friends=%s WHERE user_id=%s;"
                    # 要删除好友所需的参数
                    params = [friend_str, user.user_id]
                    # 执行sql语句
                    self.cursor.execute(delete_friend_sql, params)
                    logger.info("用户{}删除好友{}成功！".format(user.user_id, friend.user_id))
                    return SUCCESS
                else:
                    return NOT_FRIEND
            except Exception as e:
                self.connect.rollback()
                logger.exception("用户{}删除好友{}失败！原因：{}".format(user.user_id, friend.user_id, e))
                return ERROR
            finally:
                # 提交执行操作
                self.connect.commit()
        else:
            return USER_NOT_EXIST

    def find_user_friends(self, user):
        """
        查询用户好友
        :param user:
        :return:
        """
        # 判断用户是否存在
        if self.find_user(user):
            try:
                # 查询用户好友的sql语句
                find_user_friends_sql = "SELECT * FROM user_friends WHERE user_id=%s;"
                # 要查询用户好友的用户
                params = [user.user_id]
                # 执行sql语句
                self.cursor.execute(find_user_friends_sql, params)
                # 获取查询结果
                find_user_friends_result = self.cursor.fetchone()
                # 取查询结果中的第二个字段:friends
                if "friends" in find_user_friends_result and find_user_friends_result["friends"]:
                    # 取好友列表字段
                    friend_str = find_user_friends_result["friends"]
                    # 将用户好友字段转化为列表
                    friend_list = friend_str.split(",")
                else:
                    # 若查询不到,则默认好友列表为空
                    friend_list = []
                # 用集合来存储用户好友
                friend_set = set(friend_list)
                # 返回查询结果
                return friend_set
            except Exception as e:
                logger.exception(e)
        else:
            return USER_NOT_EXIST


class DbUserInfo(DbUserFriends):
    """
    对user_info表进行改查的操作
    """

    def update_user_info(self, user):
        """
        修改用户信息
        :param user:
        :return:
        """
        # 判断用户是否存在
        if self.find_user(user):
            try:
                # 获取用户的各项信息
                user_info_message = user.__dict__
                # 删除多余的用户信息
                user_id = user_info_message.pop("user_id")
                user_info_message.pop("password")
                # 修改用户信息的sql语句
                update_info_sql = "UPDATE user_info SET "
                # 要修改的用户信息参数
                params = []
                for key in user_info_message:
                    if user_info_message[key] is not None:
                        update_info_sql += key + "=%s,"
                        params.append(user_info_message[key])
                # 添加要修改用户信息的sql语句判断条件
                update_info_sql = update_info_sql[:-1] + " WHERE user_id=%s;"
                params.append(user_id)
                # 执行sql语句
                self.cursor.execute(update_info_sql, params)
                logger.info("用户{}信息修改成功！".format(user_id))
                return SUCCESS
            except Exception as e:
                self.connect.rollback()
                logger.exception("用户{}信息修改失败！原因：{}".format(user.user_id, e))
                return ERROR
            finally:
                # 提交执行操作
                self.connect.commit()
        else:
            return USER_NOT_EXIST

    def find_user_info(self, user):
        """
        查询用户信息
        :param user:
        :return:
        """
        if self.find_user(user):
            # 查询此用户信息的sql语句
            find_sql = "SELECT * FROM user_info WHERE user_id=%s;"
            # 获取此用户信息
            params = [user.user_id]
            # 执行sql语句
            self.cursor.execute(find_sql, params)
            # 获取用户信息
            user_info = self.cursor.fetchone()
            # 若图片路径不为空，则补全图片路径
            if user_info["image"]:
                user_info["image"] = BASE_URL + user_info["image"]
            # 若出生日期存在，则将日期对象转化为字符串
            if user_info["birthday"]:
                user_info["birthday"] = str(user_info["birthday"])
            # 返回用户信息
            return user_info
        else:
            return USER_NOT_EXIST

    def find_user_friends_info(self, user):
        """
        查询用户好友信息
        :param user:
        :return:
        """
        # 判断用户是否存在
        if self.find_user(user):
            # 用户好友信息列表
            friend_info_list = []
            # 用户好友列表
            friend_set = self.find_user_friends(user)
            # 依次查询各个好友信息
            for friend in friend_set:
                # 将用户好友字符串转化为对象
                _friend = User(friend, "")
                # 查询单个好友信息
                friend_info = self.find_user_info(_friend)
                # 判断是否获取到信息
                if friend_info:
                    # 将信息添加到列表中
                    friend_info_list.append(friend_info)
            # 返回用户好友信息列表
            return friend_info_list
        else:
            return USER_NOT_EXIST

    def find_user_online_info(self, user):
        """
        查询在线用户
        :return:
        """
        # 获取查询信息
        return self.find_all_user_info(user, online=True)

    def find_all_user_info(self, user, online=False):
        """
        查询所有用户
        :param user:
        :param online:
        :return:
        """
        try:
            # 判断是否查询在线用户
            if online:
                # 查询除了此用户的所有在线用户信息的sql语句
                find_sql = "SELECT * FROM user_info WHERE online=1 and user_id!=%s;"
            else:
                # 查询此用户信息的sql语句
                find_sql = "SELECT * FROM user_info WHERE user_id!=%s;"
            # 查看用户信息的参数
            params = [user.user_id]
            # 执行sql语句
            self.cursor.execute(find_sql, params)
            # 获取所有用户信息
            all_user_info = self.cursor.fetchall()
            for user_info in all_user_info:
                # 若图片路径不为空，则补全图片路径
                if user_info["image"]:
                    user_info["image"] = BASE_URL + user_info["image"]
                # 若出生日期存在，则将日期对象转化为字符串
                if user_info["birthday"]:
                    user_info["birthday"] = str(user_info["birthday"])
            # 返回所有用户信息
            return all_user_info

        except Exception as e:
            logger.exception(e)


class DbSendMessage(DbUserInfo):
    """
      对"SEND_MESSAGE"表进行增删改查的操作
    """

    def add_message(self, sender, receiver, message=None, request=SEND_MESSAGE):
        """
        发送信息或请求
        :param sender:
        :param receiver:
        :param request:
        :param message:
        :return:
        """
        # 判断发送者和接受者是否存在
        if self.find_user(sender) and self.find_user(receiver):
            # 获取发送者和接受者的好友列表
            sender_friends = self.find_user_friends(sender)
            receiver_friends = self.find_user_friends(receiver)
            # 判断两者是否是好友
            if sender.user_id in receiver_friends and receiver.user_id in sender_friends:
                # 判断是否是发送请求
                if request == SEND_REQUEST:
                    return IS_FRIEND
            else:
                # 判断是否是发送信息
                if request == SEND_MESSAGE:
                    return NOT_FRIEND
            try:
                if request is not SEND_MESSAGE:
                    # 查询是否存在请求语句
                    select_message_sql = "SELECT * FROM send_message WHERE sender=%s AND receiver=%s;"
                    # 查询是否存在请求所需的参数
                    params = [sender.user_id, receiver.user_id]
                    # 执行sql语句
                    self.cursor.execute(select_message_sql, params)
                    # 获取执行结果
                    result = self.cursor.fetchall()
                    # 判断是否存在请求
                    if result:
                        # 删除当前请求语句
                        delete_message_sql = "DELETE FROM send_message WHERE sender=%s AND receiver=%s;"
                        # 删除当前请求所需的参数
                        params = [sender.user_id, receiver.user_id]
                        # 执行sql语句
                        self.cursor.execute(delete_message_sql, params)
                # 发送消息的sql语句
                add_message_sql = "INSERT INTO send_message (sender,receiver,message,request) VALUES(%s,%s,%s,%s);"
                # 发送消息所需的参数
                params = [sender.user_id, receiver.user_id, message, request]
                # 执行sql语句
                self.cursor.execute(add_message_sql, params)
                if request == SEND_MESSAGE:
                    logger.info("用户{}向用户{}发送消息成功！".format(sender.user_id, receiver.user_id))
                else:
                    logger.info("用户{}向用户{}发送添加好友请求成功！".format(sender.user_id, receiver.user_id))
                return SUCCESS
            except Exception as e:
                self.connect.rollback()
                if request == "SEND_MESSAGE":
                    logger.exception("用户{}向用户{}发送消息失败！原因：{}".format(sender.user_id, receiver.user_id, e))
                else:
                    logger.exception("用户{}向用户{}发送请求失败！原因：{}".format(sender.user_id, receiver.user_id, e))
                return ERROR
            finally:
                # 提交执行操作
                self.connect.commit()
        else:
            return USER_NOT_EXIST

    def delete_message(self, sender, receiver):
        """
        删除信息或请求
        :param sender:
        :param receiver:
        :return:
        """
        # 判断发送者和接受者是否存在
        if self.find_user(sender) and self.find_user(receiver):
            try:
                # 删除信息的SQL语句
                delete_message_sql = "DELETE FROM send_message WHERE sender=%s AND receiver=%s;"
                # 要删除信息所需的参数
                params = [sender.user_id, receiver.user_id]
                # 执行sql语句
                self.cursor.execute(delete_message_sql, params)
                return SUCCESS
            except Exception as e:
                self.connect.rollback()
                logger.exception("用户{}与用户{}的消息删除失败！原因：{}".format(receiver.user_id, sender.user_id, e))
                return ERROR
            finally:
                # 提交执行操作
                self.connect.commit()
        else:
            return USER_NOT_EXIST

    def delete_message_info(self, receiver):
        """
        删除请求通知
        :param receiver:
        :return:
        """
        if self.find_user(receiver):
            try:
                # 删除信息的SQL语句
                delete_message_sql = "DELETE FROM send_message WHERE receiver=%s AND (request=%s OR request=%s);"
                # 要删除信息所需的参数
                params = [receiver.user_id, AGREE_REQUEST, REFUSE_REQUEST]
                # 执行sql语句
                self.cursor.execute(delete_message_sql, params)
                return SUCCESS
            except Exception as e:
                self.connect.rollback()
                logger.exception("用户{}的消息删除失败！原因：{}".format(receiver.user_id, e))
                return ERROR
            finally:
                # 提交执行操作
                self.connect.commit()
        else:
            return USER_NOT_EXIST

    def update_request(self, sender, receiver, request):
        """
        更新请求
        :param sender:
        :param receiver:
        :param request:
        :return:
        """
        # 判断用户是否存在
        if self.find_user(sender) and self.find_user(receiver):
            try:
                # 修改用户请求的sql语句
                update_request_sql = "UPDATE send_message SET request=%s WHERE sender=%s AND receiver=%s;"
                # 修改用户请求所需的参数
                params = [request, sender.user_id, receiver.user_id]
                # 执行sql语句
                self.cursor.execute(update_request_sql, params)
                logger.info("用户{}对用户{}的请求修改成功！".format(sender.user_id, receiver.user_id))
                return SUCCESS
            except Exception as e:
                self.connect.rollback()
                logger.exception("用户{}对用户{}的请求修改失败！原因：{}".format(sender.user_id, receiver.user_id, e))
                return ERROR
            finally:
                # 提交执行操作
                self.connect.commit()
        else:
            return USER_NOT_EXIST

    def find_message(self, receiver):
        """
        查看信息
        :param receiver:
        :return:
        """
        # 查询信息
        return self.find_info(receiver, SEND_MESSAGE)

    def find_request(self, receiver):
        """
        查看请求
        :param receiver:
        :return:
        """
        # 查询请求
        return self.find_info(receiver, SEND_REQUEST)

    def find_message_info(self, receiver):
        """
        查看消息通知
        :param receiver:
        :return:
        """
        try:
            # 查看信息的sql语句
            find_message_sql = "SELECT * FROM send_message WHERE receiver=%s AND (request=%s OR request=%s);"
            # 查询消息所需的参数
            params = [receiver.user_id, AGREE_REQUEST, REFUSE_REQUEST]
            # 执行sql语句
            self.cursor.execute(find_message_sql, params)
            # 获取查询结果
            message_str = self.cursor.fetchall()
            for message in message_str:
                # 若出生日期存在，则将日期对象转化为字符串
                if message["date_time"]:
                    message["date_time"] = str(message["date_time"])
            # 返回查询结果
            return message_str
        except Exception as e:
            logger.exception("用户{}的信息查看失败！原因：{}".format(receiver.user_id, e))

    def find_info(self, receiver, request):
        """
        查看信息和请求
        :param receiver:
        :param request:
        :return:
        """
        try:
            # 查看信息的sql语句
            find_message_sql = "SELECT * FROM send_message WHERE receiver=%s AND request=%s;"
            # 查询消息所需的参数
            params = [receiver.user_id, request]
            # 执行sql语句
            self.cursor.execute(find_message_sql, params)
            # 获取查询结果
            message_str = self.cursor.fetchall()
            for message in message_str:
                # 若出生日期存在，则将日期对象转化为字符串
                if message["date_time"]:
                    message["date_time"] = str(message["date_time"])
            # 返回查询结果
            return message_str
        except Exception as e:
            logger.exception("用户{}的信息查看失败！原因：{}".format(receiver.user_id, e))


class MySQL(DbSendMessage):
    """
    对所有数据库进行操作
    """
