# /usr/bin/python
# -*- coding:utf-8 -*-
import redis
from proxypool.config import DB_HOST,DB_PORT,DB_PASSWORD # redis数据库的配置
from proxypool.error import PoolEmptyError # 取代理时为空的异常处理
class RedisConnect(object):
    _db = None
    def __init__(self):
        if DB_PASSWORD:
            self._db = redis.Redis(host=DB_HOST, port=DB_PORT, password=DB_PASSWORD)
        else:
            self._db = redis.Redis(host=DB_HOST, port=DB_PORT)

    def get(self,count=1):
        '''
            从左边获取代理地址，默认第一个，然后删除
        '''
        proxies = self._db.lrange("proxies", 0, count - 1) # 从左边第一个元素开始，获取要获取的元素个数
        self._db.ltrim("proxies", count, -1) # 只保留结束位置到倒数第一个的列表元素，等同于删除刚刚取出的元素
        return proxies

    def put(self,proxy):
        ''' 从右边插入可用的代理 '''
        self._db.rpush('proxies',proxy)

    def pop(self):
        ''' 从右边取出一个元素，并删除，如果没有获取到则引发一个代理为空的异常 '''
        try:
            return self._db.rpop("proxies").decode('utf-8')
        except:
            raise PoolEmptyError

    @property # @property的作用是将一个类方法变成一个类属性 重新实现一个该属性的获取和修改的方法
    def queue_len(self):
        """
        获取队列的长度
        """
        return self._db.llen("proxies")

    def flush(self):
        """
        刷新数据库
        """
        self._db.flushall()

def main():
    r = RedisConnect()
    a = r.queue_len
    print(a)


if __name__ == '__main__':
    main()
