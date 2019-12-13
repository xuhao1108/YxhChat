import os

# 登录窗口标题
LOGIN_TITLE = "YxhChat"
# 登录窗口尺寸
LOGIN_WIDTH = 300
LOGIN_HEIGHT = 317
HIDE_HEIGHT = 100
REGISTER_WIDTH = 300
REGISTER_HEIGHT = 150
# 聊天窗口尺寸
CHAT_WIDTH = 900
CHAT_HEIGHT = 700

# 缓存文件默认路径
CACHE_FILE_PATH = os.path.dirname(__file__) + "/Pane"
# 请求的根URL地址
BASE_URL = "http://0.0.0.0:5000/"
SOCKET_URL = "ws://0.0.0.0:5000/"

# 登录成功标记
DESTROY_ROOT = "DESTROY_ROOT"
LOGIN_SUCCESS = "LOGIN_SUCCESS"
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
