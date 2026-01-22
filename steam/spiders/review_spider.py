import re

import scrapy
from scrapy.http import FormRequest, Request
from w3lib.url import url_query_parameter

from ..items import ReviewItem, ReviewItemLoader, str_to_int


def load_review(review, product_id, page, order):
    """
    从单个评论元素中加载 ReviewItem。
    :param review: 评论的 HTML 元素选择器
    :param product_id: 游戏 ID
    :param page: 当前页码
    :param order: 当前页内的排序
    """
    loader = ReviewItemLoader(ReviewItem(), review)

    loader.add_value('product_id', product_id)
    loader.add_value('page', page)
    loader.add_value('page_order', order)

    # 提取评论基本数据
    loader.add_css('recommended', '.title::text') # 推荐/不推荐
    loader.add_css('date', '.date_posted::text', re='Posted: (.+)') # 发布日期
    loader.add_css('text', '.apphub_CardTextContent::text') # 评论正文
    loader.add_css('hours', '.hours::text', re='(.+) hrs') # 游玩时长
    loader.add_css('compensation', '.received_compensation::text') # 是否收到补偿

    # 提取用户数据
    loader.add_css('user_id', '.apphub_CardContentAuthorName a::attr(href)', re='.*/profiles/(.+)/')
    loader.add_css('username', '.apphub_CardContentAuthorName a::text')
    loader.add_css('products', '.apphub_CardContentMoreLink ::text', re='([\d,]+) product') # 用户拥有的游戏数

    # 提取评论反馈数据（有用、无用、欢乐）
    feedback = loader.get_css('.found_helpful ::text')
    loader.add_value('found_helpful', feedback, re='([\d,]+) of')
    loader.add_value('found_unhelpful', feedback, re='of ([\d,]+)')
    loader.add_value('found_funny', feedback, re='([\d,]+).*funny')

    # 检查是否为抢先体验评论
    early_access = loader.get_css('.early_access_review')
    if early_access:
        loader.add_value('early_access', True)
    else:
        loader.add_value('early_access', False)

    return loader.load_item()


def get_page(response):
    """
    获取当前请求的页码。
    优先从 meta 数据中获取，其次从 URL 参数中提取。
    """
    from_page = response.meta.get('from_page', None)

    if from_page:
        page = from_page + 1
    else:
        page = url_query_parameter(response.url, 'p', None)
        if page:
            page = str_to_int(page)

    return page


def get_product_id(response):
    """
    获取当前请求的游戏 ID。
    优先从 meta 数据中获取，其次从 URL 中正则提取。
    """
    product_id = response.meta.get('product_id', None)

    if not product_id:
        try:
            return re.findall("app/(.+?)/", response.url)[0]
        except:  # noqa E722
            return None
    else:
        return product_id


class ReviewSpider(scrapy.Spider):
    """
    评论爬虫，专门用于抓取特定游戏的评论。
    """
    name = 'reviews'
    test_urls = [
        # 测试用 URL (Full Metal Furies)
        'http://steamcommunity.com/app/416600/reviews/?browsefilter=mostrecent&p=1',
    ]

    def __init__(self, url_file=None, steam_id=None, *args, **kwargs):
        """
        初始化爬虫。
        :param url_file: 包含 URL 列表的文件路径
        :param steam_id: 单个游戏 ID
        """
        super().__init__(*args, **kwargs)
        self.url_file = url_file
        self.steam_id = steam_id

    def read_urls(self):
        """读取 URL 文件生成请求"""
        with open(self.url_file, 'r') as f:
            for url in f:
                url = url.strip()
                if url:
                    yield scrapy.Request(url, callback=self.parse)

    def start_requests(self):
        """
        根据输入参数决定起始请求。
        优先级: steam_id > url_file > test_urls
        """
        if self.steam_id:
            url = (
                f'http://steamcommunity.com/app/{self.steam_id}/reviews/'
                '?browsefilter=mostrecent&p=1'
            )
            yield Request(url, callback=self.parse)
        elif self.url_file:
            yield from self.read_urls()
        else:
            for url in self.test_urls:
                yield Request(url, callback=self.parse)

    def parse(self, response):
        """
        解析评论列表页面。
        1. 提取当前页的所有评论。
        2. 查找并处理分页表单，获取下一页。
        """
        page = get_page(response)
        product_id = get_product_id(response)

        # 加载当前页面的所有评论
        reviews = response.css('div .apphub_Card')
        for i, review in enumerate(reviews):
            yield load_review(review, product_id, page, i)

        # 导航到下一页
        # Steam 评论分页使用表单提交而不是简单的链接
        form = response.xpath('//form[contains(@id, "MoreContentForm")]')
        if form:
            yield self.process_pagination_form(form, page, product_id)

    def process_pagination_form(self, form, page=None, product_id=None):
        """
        处理分页表单，构造下一页的请求。
        """
        action = form.xpath('@action').extract_first()
        names = form.xpath('input/@name').extract()
        values = form.xpath('input/@value').extract()

        formdata = dict(zip(names, values))
        meta = dict(prev_page=page, product_id=product_id)

        # 提交表单获取下一页数据
        return FormRequest(
            url=action,
            method='GET',
            formdata=formdata,
            callback=self.parse,
            meta=meta
        )
