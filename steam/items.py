from datetime import datetime, date
import logging

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, Join, MapCompose, TakeFirst

logger = logging.getLogger(__name__)


class StripText:
    """
    自定义文本清洗处理器
    去除字符串两端的空白字符（空格、换行、制表符等）
    """
    def __init__(self, chars=' \r\t\n'):
        self.chars = chars

    def __call__(self, value):
        try:
            return value.strip(self.chars)
        except:  # noqa E722
            return value


def simplify_recommended(x):
    """
    将推荐状态字符串转换为布尔值
    'Recommended' -> True
    其他 -> False
    """
    return True if x == 'Recommended' else False


def standardize_date(x):
    """
    标准化日期格式
    将输入日期转换为 'YYYY-MM-DD' 格式
    如果转换失败则保留原样
    """
    fmt_fail = False

    # 尝试解析带年份的完整日期
    for fmt in ['%b %d, %Y', '%B %d, %Y']:
        try:
            return datetime.strptime(x, fmt).strftime('%Y-%m-%d')
        except ValueError:
            fmt_fail = True

    # 如果年份缺失，假设为当前年份（Steam 评论常见情况）
    for fmt in ['%b %d', '%B %d']:
        try:
            d = datetime.strptime(x, fmt)
            d = d.replace(year=date.today().year)
            return d.strftime('%Y-%m-%d')
        except ValueError:
            fmt_fail = True

    if fmt_fail:
        logger.debug(f'Could not process date {x}')

    return x


def str_to_float(x):
    """
    将包含千位分隔符的字符串转换为浮点数
    例如: '1,234.56' -> 1234.56
    """
    x = x.replace(',', '')
    try:
        return float(x)
    except:  # noqa E722
        return x


def str_to_int(x):
    """
    将字符串转换为整数
    先转浮点再转整数，以处理 '1,234.0' 这样的情况
    """
    try:
        return int(str_to_float(x))
    except:  # noqa E722
        return x


class ProductItem(scrapy.Item):
    """
    定义游戏产品的数据结构
    包含游戏的基本信息、价格、评分等
    """
    url = scrapy.Field()  # 游戏商店页面 URL
    id = scrapy.Field()   # Steam App ID
    app_name = scrapy.Field() # 游戏名称（从 URL 或标题提取）
    reviews_url = scrapy.Field() # 评论页面 URL
    title = scrapy.Field() # 游戏标题
    genres = scrapy.Field( # 游戏类型标签列表
        output_processor=Compose(TakeFirst(), lambda x: x.split(','), MapCompose(StripText()))
    )
    developer = scrapy.Field() # 开发商
    publisher = scrapy.Field() # 发行商
    release_date = scrapy.Field( # 发行日期
        output_processor=Compose(TakeFirst(), StripText(), standardize_date)
    )
    specs = scrapy.Field( # 游戏特性（如单人、多人、支持手柄等）
        output_processor=MapCompose(StripText())
    )
    tags = scrapy.Field( # 用户定义的标签
        output_processor=MapCompose(StripText())
    )
    price = scrapy.Field( # 当前价格
        output_processor=Compose(TakeFirst(),
                                 StripText(chars=' $\n\t\r'),
                                 str_to_float)
    )
    discount_price = scrapy.Field( # 折后价格
        output_processor=Compose(TakeFirst(),
                                 StripText(chars=' $\n\t\r'),
                                 str_to_float)
    )
    sentiment = scrapy.Field() # 总体评价概览（如 'Very Positive'）
    n_reviews = scrapy.Field( # 总评论数
        output_processor=Compose(
            MapCompose(StripText(), lambda x: x.replace(',', ''), str_to_int),
            max
        )
    )
    metascore = scrapy.Field( # Metacritic 评分
        output_processor=Compose(TakeFirst(), StripText(), str_to_int)
    )
    early_access = scrapy.Field() # 是否为抢先体验游戏


class ReviewItem(scrapy.Item):
    """
    定义单条评论的数据结构
    """
    product_id = scrapy.Field() # 游戏 ID
    page = scrapy.Field()       # 评论所在的页码
    page_order = scrapy.Field() # 页面内的排序位置
    recommended = scrapy.Field( # 是否推荐（True=推荐, False=不推荐）
        output_processor=Compose(TakeFirst(), simplify_recommended),
    )
    date = scrapy.Field( # 评论发布日期
        output_processor=Compose(TakeFirst(), standardize_date)
    )
    text = scrapy.Field( # 评论正文内容
        input_processor=MapCompose(StripText()),
        output_processor=Compose(Join('\n'), StripText())
    )
    hours = scrapy.Field( # 游玩时长（小时）
        output_processor=Compose(TakeFirst(), str_to_float)
    )
    found_helpful = scrapy.Field( # 认为有帮助的人数
        output_processor=Compose(TakeFirst(), str_to_int)
    )
    found_unhelpful = scrapy.Field( # 认为没帮助的人数
        output_processor=Compose(TakeFirst(), str_to_int)
    )
    found_funny = scrapy.Field( # 认为有趣的次数
        output_processor=Compose(TakeFirst(), str_to_int)
    )
    compensation = scrapy.Field() # 是否收到补偿（如免费获取）
    username = scrapy.Field()     # 评论者用户名
    user_id = scrapy.Field()      # 评论者 ID
    products = scrapy.Field(      # 评论者拥有的游戏数量
        output_processor=Compose(TakeFirst(), str_to_int)
    )
    early_access = scrapy.Field() # 是否为抢先体验阶段的评论


class ProductItemLoader(ItemLoader):
    """
    产品数据的加载器
    默认取第一个非空值并去除空白
    """
    default_output_processor = Compose(TakeFirst(), StripText())


class ReviewItemLoader(ItemLoader):
    """
    评论数据的加载器
    默认取第一个非空值
    """
    default_output_processor = TakeFirst()
