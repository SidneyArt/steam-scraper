import logging
import re
from w3lib.url import canonicalize_url, url_query_cleaner

from scrapy.http import FormRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import ProductItem, ProductItemLoader

logger = logging.getLogger(__name__)


def load_product(response):
    """
    从产品页面响应中加载 ProductItem。
    这个函数负责提取页面上的各种信息并填充到 Item 对象中。
    """
    loader = ProductItemLoader(item=ProductItem(), response=response)

    # 清理 URL，移除 snr 参数并规范化
    url = url_query_cleaner(response.url, ['snr'], remove=True)
    url = canonicalize_url(url)
    loader.add_value('url', url)

    # 从 URL 中提取 App ID
    found_id = re.findall('/app/(.*?)/', response.url)
    if found_id:
        id = found_id[0]
        # 构造该游戏的评论页面 URL
        reviews_url = f'http://steamcommunity.com/app/{id}/reviews/?browsefilter=mostrecent&p=1'
        loader.add_value('reviews_url', reviews_url)
        loader.add_value('id', id)

    # 提取出版详情（开发者、发行商、日期等）
    # 这些信息通常在一个 .details_block 块中，以 <br> 分隔
    details = response.css('.details_block').extract_first()
    try:
        details = details.split('<br>')

        for line in details:
            line = re.sub('<[^<]+?>', '', line)  # 移除 HTML 标签
            line = re.sub('[\r\t\n]', '', line).strip() # 移除空白符
            for prop, name in [
                ('Title:', 'title'),
                ('Genre:', 'genres'),
                ('Developer:', 'developer'),
                ('Publisher:', 'publisher'),
                ('Release Date:', 'release_date')
            ]:
                if prop in line:
                    item = line.replace(prop, '').strip()
                    loader.add_value(name, item)
    except:  # noqa E722
        pass

    # 使用 CSS 选择器提取其他基本信息
    loader.add_css('app_name', '.apphub_AppName ::text')
    loader.add_css('specs', '.game_area_details_specs a ::text')
    loader.add_css('tags', 'a.app_tag::text')

    # 提取价格信息
    price = response.css('.game_purchase_price ::text').extract_first()
    if not price:
        # 如果没有标准价格，可能是打折，尝试提取原价和折后价
        price = response.css('.discount_original_price ::text').extract_first()
        loader.add_css('discount_price', '.discount_final_price ::text')
    loader.add_value('price', price)

    # 提取评价概览（如 "Very Positive"）
    sentiment = response.css('.game_review_summary').xpath(
        '../*[@itemprop="description"]/text()').extract()
    loader.add_value('sentiment', sentiment)
    
    # 提取总评论数，使用正则从 "12,345 reviews" 中提取数字
    loader.add_css('n_reviews', '.responsive_hidden', re='\(([\d,]+) reviews\)')

    # 提取 Metacritic 评分
    loader.add_xpath(
        'metascore',
        '//div[@id="game_area_metascore"]/div[contains(@class, "score")]/text()')

    # 检查是否为抢先体验游戏
    early_access = response.css('.early_access_header')
    if early_access:
        loader.add_value('early_access', True)
    else:
        loader.add_value('early_access', False)

    return loader.load_item()


class ProductSpider(CrawlSpider):
    """
    产品爬虫，用于抓取 Steam 商店的游戏信息。
    继承自 CrawlSpider，可以定义规则自动跟踪链接。
    """
    name = 'products'
    # 起始 URL：按发行日期降序排列的游戏列表
    start_urls = ['http://store.steampowered.com/search/?sort_by=Released_DESC']

    allowed_domains = ['steampowered.com']

    # 定义爬取规则
    rules = [
        # 规则 1：匹配游戏详情页 URL (/app/...)，并调用 parse_product 进行解析
        Rule(LinkExtractor(
             allow='/app/(.+)/',
             restrict_css='#search_result_container'),
             callback='parse_product'),
        # 规则 2：匹配分页链接 (page=...)，自动跟进下一页列表
        Rule(LinkExtractor(
             allow='page=(\d+)',
             restrict_css='.search_pagination_right'))
    ]

    def __init__(self, steam_id=None, *args, **kwargs):
        """
        初始化爬虫。
        :param steam_id: 可选参数，如果提供，则只抓取指定 ID 的游戏。
        """
        super().__init__(*args, **kwargs)
        self.steam_id = steam_id

    def start_requests(self):
        """
        开始请求。
        如果指定了 steam_id，则直接请求该游戏页面；否则使用 start_urls 开始遍历。
        """
        if self.steam_id:
            yield Request(f'http://store.steampowered.com/app/{self.steam_id}/',
                          callback=self.parse_product)
        else:
            yield from super().start_requests()

    def parse_product(self, response):
        """
        解析产品页面。
        处理年龄验证跳转，或调用 load_product 提取数据。
        """
        # 检查是否遇到年龄验证页面
        if '/agecheck/app' in response.url:
            logger.debug(f'Form-type age check triggered for {response.url}.')

            # 提取年龄验证表单信息
            form = response.css('#agegate_box form')

            action = form.xpath('@action').extract_first()
            name = form.xpath('input/@name').extract_first()
            value = form.xpath('input/@value').extract_first()

            # 构造表单数据，伪造出生日期为 1955-01-01
            formdata = {
                name: value,
                'ageDay': '1',
                'ageMonth': '1',
                'ageYear': '1955'
            }

            # 提交表单
            yield FormRequest(
                url=action,
                method='POST',
                formdata=formdata,
                callback=self.parse_product # 验证通过后再次回调自身
            )

        else:
            # 正常页面，提取数据
            yield load_product(response)
