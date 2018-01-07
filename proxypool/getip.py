import requests
import re
from pyquery import PyQuery as pq
from proxypool.tool import getpage
class ProxyMetaclass(type):
    """
        元类，在FreeProxyGetter类中加入
        __GetIpFunc__和__GetIpFuncCount__
        两个参数，分别表示爬虫函数，和爬虫函数的数量。
    """
    def __new__(cls, name, bases, attrs):
        count = 0
        attrs['__GetIpFunc__'] = []
        for k, v in attrs.items():
            if 'getip_' in k:
                attrs['__GetIpFunc__'].append(k)
                count += 1
        attrs['__GetIpFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)

class FreeProxyGetter(object,metaclass=ProxyMetaclass):
    # 调用爬虫方法 获取所有的代理形成列表返回
    def get_raw_proxies(self, callback):
        proxies = []
        print('Callback', callback)
        for proxy in eval("self.{}()".format(callback)):
            print('Getting', proxy, 'from', callback)
            proxies.append(proxy)
        return proxies

    # 所有的方法都要生成一个生成器 供get_raw_proxies方法循环加入到数组中
    def getip_ip181(self):
        url = 'http://www.ip181.com'
        html = getpage(url)
        if html:
            parrent = re.compile('<tr.*?>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?</tr>',re.S)
            test = parrent.findall(html)[1:]
            for address,port in test:
                result = address + ':' + port
                yield result.replace(' ','')

    def getip_xicidaili(self):
        for page in range(1,4):
            url = 'http://www.xicidaili.com/wt/{}'.format(page)
            html = getpage(url)
            if html:
                doc = pq(html)
                tr = doc('tr')
                for tds in tr.items():
                    address = tds.find('td').eq(1).text()
                    port = tds.find('td').eq(2).text()
                    if address and port:
                        result = address + ':' + port
                        yield result.replace(' ','')

    def getip_ip3366(self):
        for page in range(1,4):
            url = 'http://www.ip3366.net/free/?stype=1&page={}' . format(page)
            html = getpage(url)
            if html:
                parrent = re.compile('<tr>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?</tr>',re.S)
                res = parrent.findall(html)
                for address,port in res:
                    result = '{0}:{1}'.format(address,port)
                    yield result.replace(' ','')

    def getip_66ip(self):
        for page in range(1,4):
            url = 'http://www.66ip.cn/{}.html'.format(page)
            html = getpage(url)
            if html:
                doc = pq(html)
                res = doc('#main table tr:gt(0)').items()
                for re in res:
                    address = re.find('td').eq(0).text()
                    port = re.find('td').eq(1).text()
                    if address and port:
                        result = '{0}:{1}'.format(address,port)
                        yield result.replace(' ','')

    def getip_goubanjia(self):
        for page in range(1,4):
            url = 'http://www.goubanjia.com/free/index{}.shtml'.format(page)
            html = getpage(url)
            if html:
                doc = pq(html)
                tds = doc('.ip').items()
                for td in tds:
                    td.find('p').remove()
                    yield td.text().replace(' ','')


def main():
    free = FreeProxyGetter()
    # 获取所有方法调用的网站的返回结果 每一个网站都是返回一个 list
    # wode = []
    # for callback in range(free.__GetIpFuncCount__):
    #     res = free.get_raw_proxies(free.__GetIpFunc__[callback])
    #     wode.append(res)
    # print(wode)

if __name__ == '__main__':
    main()
