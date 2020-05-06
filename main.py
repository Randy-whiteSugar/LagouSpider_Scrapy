#import os
from scrapy.cmdline import execute

# os.system("python D:\Pycharm\projectspace\proxy_pool\proxy_pool\cli\proxyPool.py schedule")
# os.system("python D:\Pycharm\projectspace\proxy_pool\proxy_pool\cli\proxyPool.py webserver")
execute('scrapy crawl lagou_spider -o jobs.csv'.split())

