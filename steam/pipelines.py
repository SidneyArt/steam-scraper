# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class SteamPipeline(object):
    """
    Steam 数据处理管道
    目前只是一个占位符，没有实际的数据处理逻辑
    可以在这里添加保存到数据库或文件的代码
    """
    def process_item(self, item, spider):
        # 默认直接返回 item，交给后续管道或 Feed Export 处理
        return item
