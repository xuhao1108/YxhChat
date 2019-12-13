import threading
import time


class MyThread(threading.Thread):
    """
    重写多线程方法，使其带返回值
    """

    def __init__(self, func, *args, **kwargs):
        """
        线程初始化
        :param func:
        :param args:
        :param name:
        """
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None

    def run(self):
        """
        重写run方法, 接收函数返回值
        :return:
        """
        self.result = self.func(*self.args, **self.kwargs)

    def get_result(self):
        """
        获取多线程的返回值
        :return:
        """
        try:
            return self.result
        except Exception as e:
            print(e)
            return None


def cc(a, b, c):
    time.sleep(2)
    print("******")
    print(a)
    print(b)
    print(c)
    return a + b + c


if __name__ == '__main__':
    t = MyThread(cc, 1, 2, 3)
    t.start()
    t.join()
    r = t.get_result()
    print(r)
