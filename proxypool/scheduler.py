# /usr/bin/python
# -*- coding:utf-8 -*-
import time # 时间函数
from multiprocessing import Process # 实现多进程的内置库
import asyncio  # 实现异步的库
import aiohttp  # 基于asyncio的http框架
# 关于aiohttp的异常处理
try:
    from aiohttp.errors import ProxyConnectionError,ServerDisconnectedError,ClientResponseError,ClientConnectorError
except:
    from aiohttp import ClientProxyConnectionError as ProxyConnectionError,ServerDisconnectedError,ClientResponseError,ClientConnectorError
from proxypool.db import RedisConnect # 引入数据库操作类
from proxypool.error import ResourceDepletionError # 引入数据枯竭异常类
from proxypool.getip import FreeProxyGetter # 引入代理获取类
from proxypool.config import * # 引入所以配置项
from asyncio import TimeoutError # 引入异步处理时间超时异常处理类

# 定义一个代理检验类
class ValidityTester(object):
    test_api = TEST_API

    def __init__(self):
        self._raw_proxy = None # 用于存储获取到的待检验代理
        self._usable_proxy = [] # 用于存储检验后可用的代理列表

    # 设置待检测代理与数据库连接
    def set_raw_proxy(self,proxy):
        self._raw_proxy = proxy
        self._conn = RedisConnect()

   
    async def test_signle_proxy(self,proxy): # 声明这是一个异步函数
        ''' 检验代理将其加入到数据库中  '''
        try:
            async with aiohttp.ClientSession() as session: 
                try:
                    if isinstance(proxy,bytes):
                        proxy = proxy.decode('utf-8')
                    real_proxy = 'http://' + proxy
                    print('正在检验',proxy)
                    async with session.get(self.test_api,proxy=real_proxy,timeout=get_proxy_timeout) as response: 
                        if response.status == 200:
                            self._conn.put(proxy)
                            print('检验成功',proxy)
                except (ProxyConnectionError, TimeoutError, ValueError):
                    print('该代理无法使用',proxy)
        except (ServerDisconnectedError, ClientResponseError,ClientConnectorError) as s:
            print(s)
            pass
    
    def test(self):
        ''' 并发检验所有的代理 '''
        try:
            loop = asyncio.get_event_loop()
            tasks = [self.test_signle_proxy(proxy) for proxy in self._raw_proxy]
            loop.run_until_complete(asyncio.wait(tasks))
        except ValueError:
            print('异步并发操作失败')
        

# 该类用于获取代理加入到队列中
class ProxyAdder(object):

    def __init__(self,threshold):
        self._dbconnect = RedisConnect()
        self._getproxy = FreeProxyGetter()
        self._proxylist = []
        self._test = ValidityTester()
        self._threshold = threshold

    def is_over_threshold(self):
        """
        判断是否溢出.
        """
        if self._dbconnect.queue_len >= self._threshold:
            return True
        else:
            return False

    def add_proxy_queue(self):
        print('获取器开始工作')
        proxy_count = 0
        # 这里就一直调用从网站获取代理的方法 直到代理池饱和了 就不调用了
        while not self.is_over_threshold(): 
            for callback in range(self._getproxy.__GetIpFuncCount__):
                res = self._getproxy.get_raw_proxies(self._getproxy.__GetIpFunc__[callback])
                self._test.set_raw_proxy(res)
                self._test.test()
                proxy_count += len(res)
                # 判断是否饱和 饱和了就结束从网站获取代理的这个for循环
                if self.is_over_threshold():
                    print('IP 已经饱和等待使用')
                    break
            if proxy_count == 0:
                raise ResourceDepletionError

class Schedule(object):

    @staticmethod
    def valid_proxy():
        conn = RedisConnect()
        test = ValidityTester()
        while True:
            count = int(conn.queue_len * 0.5)
            if count == 0:
                print('等待Ip池的数据加入')
                time.sleep(POOL_LEN_CHECK_CYCLE)
                continue
            proxy_list = conn.get(count)
            test.set_raw_proxy(proxy_list)
            test.test()
            time.sleep(POOL_LEN_CHECK_CYCLE)


    @staticmethod
    def check_pool(lower_threshold=POOL_LOWER_THRESHOLD,
                   upper_threshold=POOL_UPPER_THRESHOLD,
                   cycle=POOL_LEN_CHECK_CYCLE):
        """
        如果代理的数量小于最低阈值，则添加代理
        """
        conn = RedisConnect()
        adder = ProxyAdder(upper_threshold)
        # 循环检测代理池的代理数量如果小于了最低限度 就开始工作 每20秒检测一次
        while True:
            if conn.queue_len < lower_threshold:
                adder.add_proxy_queue()
            time.sleep(cycle)

    def run(self):
        print('Ip 池维护开始工作')
        # 获取两个进程 target的意思是 该进程要运行的函数
        valid_process = Process(target=Schedule.valid_proxy)
        check_process = Process(target=Schedule.check_pool)
        # 开启进程
        valid_process.start()
        check_process.start()

def main():
    s = Schedule()
    s.run()

if __name__ == '__main__':
    main()




