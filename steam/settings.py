from smart_getenv import getenv

# 项目名称
BOT_NAME = 'steam'

# 爬虫模块列表
SPIDER_MODULES = ['steam.spiders']
NEWSPIDER_MODULE = 'steam.spiders'

# 默认 User-Agent，可以设置为浏览器的 UA 以防被封
USER_AGENT = 'Steam Scraper'

# 遵守 robots.txt 协议
ROBOTSTXT_OBEY = True

# 启用的下载中间件
DOWNLOADER_MIDDLEWARES = {
    # 禁用默认的重定向中间件，改用自定义的绕过年龄验证中间件
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'steam.middlewares.CircumventAgeCheckMiddleware': 600,
}

# 启用自动限速 (AutoThrottle)
# 自动根据 Steam 的服务器响应调整抓取速度
AUTOTHROTTLE_ENABLED = True

# 自定义去重过滤器，移除 snr 追踪参数
DUPEFILTER_CLASS = 'steam.middlewares.SteamDupeFilter'

# 启用 HTTP 缓存，加快开发调试速度
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0  # 永不过期
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [301, 302, 303, 306, 307, 308]
# 使用自定义缓存存储，移除 snr 追踪参数
HTTPCACHE_STORAGE = 'steam.middlewares.SteamCacheStorage'

# AWS 凭证，用于数据上传到 S3
AWS_ACCESS_KEY_ID = getenv('AWS_ACCESS_KEY_ID', type=str, default=None)
AWS_SECRET_ACCESS_KEY = getenv('AWS_SECRET_ACCESS_KEY', type=str, default=None)

# 导出数据编码格式
FEED_EXPORT_ENCODING = 'utf-8'
