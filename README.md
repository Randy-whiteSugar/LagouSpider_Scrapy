# LagouSpider_Scrapy
使用Scrapy编写的拉勾网爬虫，添加了代理IP池、增量爬取、自动去重（布隆过滤器：搜索关键词+URL）机制

代理IP池使用开源代码 https://github.com/WiseDoge/ProxyPool
在此提出感谢！本项目使用者请先下载该代理IP池并加以配置。

依赖中的bloom-filter使用pip直接安装会出现问题，建议从https://pypi.org/project/bloom-filter/
下载并安装，亲测可用。

如对本项目有疑问欢迎与我交流，可直接提交Issue，本人会在第一时间予以回复。
如果本项目对你有所帮助，欢迎在右上角Star我的项目，谢谢！
