import time
import random
import requests
import re
import js2py


from core.proxy_spider.base_spider import BaseSpider
from utils.http import get_request_headers

"""
1. 实现西刺代理爬虫: http://www.xicidaili.com/nn/1
    定义一个类,继承通用爬虫类(BasicSpider)
    提供urls, group_xpath 和 detail_xpath
"""


class XiciSpider(BaseSpider):
    # 准备URL列表
    urls = ['https://www.xicidaili.com/nn/{}'.format(i) for i in range(1, 11)]
    # 分组的XPATH, 用于获取包含代理IP信息的标签列表
    group_xpath = '//*[@id="ip_list"]/tr[position()>1]'
    # 组内的XPATH, 用于提取 ip, port, area
    detail_xpath = {
        'ip': './td[2]/text()',
        'port': './td[3]/text()',
        'area': './td[4]/a/text()'
    }


"""
2. 实现ip3366代理爬虫: http://www.ip3366.net/free/?stype=1&page=1
    定义一个类,继承通用爬虫类(BasicSpider)
    提供urls, group_xpath 和 detail_xpath
"""


class Ip3366Spider(BaseSpider):
    # 准备URL列表
    urls = ['http://www.ip3366.net/free/?stype={}&page={}'.format(i, j) for i in range(1, 4, 2) for j in range(1, 8)]
    # # 分组的XPATH, 用于获取包含代理IP信息的标签列表
    group_xpath = '//*[@id="list"]/table/tbody/tr'
    # 组内的XPATH, 用于提取 ip, port, area
    detail_xpath = {
        'ip': './td[1]/text()',
        'port': './td[2]/text()',
        'area': './td[5]/text()'
    }



"""
3. 实现快代理爬虫: https://www.kuaidaili.com/free/inha/1/
    定义一个类,继承通用爬虫类(BasicSpider)
    提供urls, group_xpath 和 detail_xpath
"""


class KaiSpider(BaseSpider):
    # 准备URL列表
    urls = ['https://www.kuaidaili.com/free/inha/{}/'.format(i) for i in range(1, 6)]
    # # 分组的XPATH, 用于获取包含代理IP信息的标签列表
    group_xpath = '//*[@id="list"]/table/tbody/tr'
    # 组内的XPATH, 用于提取 ip, port, area
    detail_xpath = {
        'ip':'./td[1]/text()',
        'port':'./td[2]/text()',
        'area':'./td[5]/text()'
    }

    # 当我们两个页面访问时间间隔太短了, 就报错了; 这是一种反爬手段.
    def get_page_from_url(self, url):
        # 随机等待1,3s
        time.sleep(random.uniform(1, 3))
        # 调用父类的方法, 发送请求, 获取响应数据
        return super().get_page_from_url(url)


"""
4. 实现proxylistplus代理爬虫: https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1
    定义一个类,继承通用爬虫类(BasicSpider)
    提供urls, group_xpath 和 detail_xpath
"""


class ProxylistplusSpider(BaseSpider):
    # 准备URL列表
    urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-{}'.format(i) for i in range(1, 7)]
    # # 分组的XPATH, 用于获取包含代理IP信息的标签列表
    group_xpath = '//*[@id="page"]/table[2]/tr[position()>2]'
    # 组内的XPATH, 用于提取 ip, port, area
    detail_xpath = {
        'ip': './td[2]/text()',
        'port': './td[3]/text()',
        'area': './td[5]/text()'
    }


"""
5. 实现66ip爬虫: http://www.66ip.cn/1.html
    定义一个类,继承通用爬虫类(BasicSpider)
    提供urls, group_xpath 和 detail_xpath
    由于66ip网页进行js + cookie反爬, 需要重写父类的get_page_from_url方法
"""


class Ip66Spider(BaseSpider):
    # 准备URL列表
    urls = ['http://www.66ip.cn/{}.html'.format(i) for i in range(1, 11)]
    # # 分组的XPATH, 用于获取包含代理IP信息的标签列表
    group_xpath = '//*[@id="main"]/div/div[1]/table/tr[position()>1]'
    # 组内的XPATH, 用于提取 ip, port, area
    detail_xpath = {
        'ip': './td[1]/text()',
        'port': './td[2]/text()',
        'area': './td[3]/text()'
    }

    # 重写方法, 解决反爬问题
    def get_page_from_url(self, url):
        headers = get_request_headers()
        response = requests.get(url, headers=headers)
        if response.status_code == 521:
            # 生成cookie信息, 再携带cookie发送请求
            # 生成 `_ydclearance` cookie信息
            # 1. 确定 _ydclearance 是从哪里来的;
            # 观察发现: 这个cookie信息不使用通过服务器响应设置过来的; 那么他就是通过js生成.
            # 2. 第一次发送请求的页面中, 有一个生成这个cookie的js; 执行这段js, 生成我们需要的cookie
            # 这段js是经过加密处理后的js, 真正js在 "po" 中.
            # 提取 `jp(107)` 调用函数的方法, 以及函数
            result = re.findall('window.onload=setTimeout\("(.+?)", 200\);\s*(.+?)\s*</script> ', response.content.decode('GBK'))
            # print(result)
            # 我希望执行js时候, 返回真正要执行的js
            # 把 `eval("qo=eval;qo(po);")` 替换为 return po
            func_str = result[0][1]
            func_str = func_str.replace('eval("qo=eval;qo(po);")', 'return po')
            # print(func_str)
            # 获取执行js的环境
            context = js2py.EvalJs()
            # 加载(执行) func_str
            context.execute(func_str)
            # 执行这个方法, 生成我们需要的js
            # code = gv(50)
            context.execute('code = {};'.format(result[0][0]))
            # 打印最终生成的代码
            # print(context.code)
            cookie_str = re.findall("document.cookie='(.+?); ", context.code)[0]
            # print(cookie_str)
            headers['Cookie'] = cookie_str
            response = requests.get(url, headers=headers)
            return response.content.decode('GBK')
        else:
            return response.content.decode('GBK')


if __name__ == '__main__':
    # spider = XiciSpider()
    # spider = Ip3366Spider()
    # spider = KaiSpider()
    # spider = ProxylistplusSpider()

    spider = Ip66Spider()
    for proxy in spider.get_proxies():
        print(proxy)

    # print(Ip3366Spider.urls)

    # # 测试: http://www.66ip.cn/1.html
    # url = 'http://www.66ip.cn/1.html'
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    #     # 'Cookie': '_ydclearance=35fd4248c8889feb58597e27-a31e-4f84-9edc-f1a22c16a949-1546164684;'
    # }
    # response = requests.get(url, headers=headers)
    # print(response.status_code)
    # text = response.content.decode('GBK')
    #
    # # 生成 `_ydclearance` cookie信息
    # # 1. 确定 _ydclearance 是从哪里来的;
    # # 观察发现: 这个cookie信息不使用通过服务器响应设置过来的; 那么他就是通过js生成.
    # # 2. 第一次发送请求的页面中, 有一个生成这个cookie的js; 执行这段js, 生成我们需要的cookie
    # # 这段js是经过加密处理后的js, 真正js在 "po" 中.
    # # 提取 `jp(107)` 调用函数的方法, 以及函数
    # result = re.findall('window.onload=setTimeout\("(.+?)", 200\);\s*(.+?)\s*</script> ' ,text)
    # # print(result)
    # # 我希望执行js时候, 返回真正要执行的js
    # # 把 `eval("qo=eval;qo(po);")` 替换为 return po
    # func_str = result[0][1]
    # func_str = func_str.replace('eval("qo=eval;qo(po);")', 'return po')
    # # print(func_str)
    # # 获取执行js的环境
    # context = js2py.EvalJs()
    # # 加载(执行) func_str
    # context.execute(func_str)
    # # 执行这个方法, 生成我们需要的js
    # # code = gv(50)
    # context.execute('code = {};'.format(result[0][0]))
    # # 打印最终生成的代码
    # # print(context.code)
    # cookie_str = re.findall("document.cookie='(.+?); ", context.code)[0]
    # # print(cookie_str)
    # headers['Cookie'] = cookie_str
    # response = requests.get(url, headers=headers)
    # print(response.content.decode('GBK'))










