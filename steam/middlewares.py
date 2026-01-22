import logging
import os
import re
from w3lib.url import url_query_cleaner

from scrapy import Request
from scrapy.downloadermiddlewares.redirect import RedirectMiddleware
from scrapy.dupefilters import RFPDupeFilter
from scrapy.extensions.httpcache import FilesystemCacheStorage
from scrapy.utils.request import request_fingerprint

logger = logging.getLogger(__name__)


def strip_snr(request):
    """
    移除 URL 中的 'snr' 查询参数并返回修改后的请求。
    'snr' 参数用于 Steam 内部追踪，去除它可以避免因追踪码不同导致重复抓取。
    """
    url = url_query_cleaner(request.url, ['snr'], remove=True)
    return request.replace(url=url)


class SteamCacheStorage(FilesystemCacheStorage):
    """
    自定义缓存存储策略。
    在计算请求指纹前先移除 'snr' 参数，确保相同页面（即使 snr 不同）能命中缓存。
    """
    def _get_request_path(self, spider, request):
        request = strip_snr(request)
        key = request_fingerprint(request)
        return os.path.join(self.cachedir, spider.name, key[0:2], key)


class SteamDupeFilter(RFPDupeFilter):
    """
    自定义去重过滤器。
    在计算指纹前移除 'snr' 参数，防止重复抓取同一页面。
    """
    def request_fingerprint(self, request):
        request = strip_snr(request)
        return super().request_fingerprint(request)


class CircumventAgeCheckMiddleware(RedirectMiddleware):
    """
    自动绕过年龄验证的中间件。
    当检测到重定向到年龄验证页面时，自动添加 'mature_content=1' cookie 并重新请求。
    """
    def _redirect(self, redirected, request, spider, reason):
        # 仅当重定向目标包含 'agecheck' 时才介入
        # 其他重定向交给默认中间件处理
        if not re.findall('app/(.*)/agecheck', redirected.url):
            return super()._redirect(redirected, request, spider, reason)

        logger.debug(f'Button-type age check triggered for {request.url}.')

        # 重新发起请求，带上 mature_content=1 的 cookie
        return Request(url=request.url,
                       cookies={'mature_content': '1'},
                       meta={'dont_cache': True},
                       callback=spider.parse_product)
