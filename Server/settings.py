import logging
import os

# 日志输出格式
LOGGER_FORMAT = "%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s"
# 日志时间输出格式
LOGGER_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
# 日志等级
LOGGER_LEVEL = logging.INFO
# 日志文件名
LOGGER_FILENAME = "log.log"
# 日志编码格式
LOGGER_ENCODING = "UTF-8"

# flask启动host
FLASK_HOST = "0.0.0.0"
# flask启动端口
FLASK_PORT = 5000
# 管理员账号
ADMIN_ID = "admin"
# 管理员密码
ADMIN_PASSWORD = "admin"

# 缓存文件默认路径
CACHE_FILE_PATH = os.path.dirname(__file__) + "/User/static/"
# 初始url路径
BASE_URL = "http://{}:{}/".format(FLASK_HOST, FLASK_PORT)

# 静态文件路径
STATIC_PATH = "static/images/user/"

# 连接mysql数据库的host
MYSQL_HOST = "localhost"
# 连接mysql数据库的用户名
MYSQL_USER = "root"
# 连接mysql数据库的密码
MYSQL_PASSWORD = "yxh981108"
# 连接mysql数据库的数据库名
MYSQL_DB = "chat"
# 执行成功的标记
SUCCESS = "SUCCESS"
# 执行失败的标记
ERROR = "ERROR"
# 用户已经存在的标记
USER_EXIST = "USER_EXIST"
# 用户不存在的标记
USER_NOT_EXIST = "USER_NOT_EXIST"
# 用户在线标记
ONLINE = "ONLINE"
# 不正确的标记
NOT_CORRECT = "NOT_CORRECT"
# 是好友的标记
IS_FRIEND = "IS_FRIEND"
# 不是好友的标记
NOT_FRIEND = "NOT_FRIEND"
# 发送消息
SEND_MESSAGE = 0
# 发送请求
SEND_REQUEST = 1
# 同意请求
AGREE_REQUEST = 2
# 拒绝请求
REFUSE_REQUEST = 3
# 上线通知
ONLINE_INFO = 4
# 下线通知
OFFLINE_INFO = 5
