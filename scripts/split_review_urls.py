"""
将抓取到的游戏产品数据加载到 DataFrame 中，并将评论 URL 分割写入 N 个文本文件。
这样做是为了将大规模的评论抓取任务拆分为多个小任务，便于并行处理或分布式抓取。

运行示例:
    $ python split_review_urls.py \
        --scraped-products $(pwd)/../output/products_.jl \
        --output-dir $(pwd)/../output
"""
import argparse
import json
import math
import os
from random import shuffle

import numpy as np
import pandas as pd


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--scraped-products',
        help='抓取到的 products.jl 文件路径。',
    )
    parser.add_argument(
        '--output-dir',
        help='生成的 URL 拆分文件存放目录。'
    )
    parser.add_argument(
        '--pieces',
        help='要拆分成多少个文件。',
        default=10
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # 读取 JSON Lines 格式的产品数据
    with open(args.scraped_products) as f:
        rows = [json.loads(l) for l in f]

    df = pd.DataFrame(rows)

    # 过滤掉无效数据：
    # 1. 必须包含 id, reviews_url, title
    # 2. 评论数必须大于 0
    blx_nontrivial = np.all(df[['id', 'reviews_url', 'title']].notnull(), axis=1)
    blx_has_reviews = df['n_reviews'] > 0
    blx = blx_nontrivial & blx_has_reviews

    # 提取符合条件的评论 URL 并去重
    urls = df.loc[blx, 'reviews_url'].unique()
    # 随机打乱顺序，避免同一类游戏集中在一起
    shuffle(urls)

    # 计算切分步长
    n = len(urls)
    step = int(math.ceil(float(n)/args.pieces))

    # 分块写入文件
    for n_part, bound in enumerate(range(0, n, step), start=1):
        file_name = os.path.join(
            args.output_dir,
            'review_urls_{:02d}.txt'.format(n_part)
        )

        with open(file_name, 'w') as f:
            piece = urls[bound:bound + step]
            f.write('\n'.join(piece))

    # 统计总共待抓取的评论数上限
    n_items = int(df.loc[blx, 'n_reviews'].sum())
    print("There are <={0} reviews to be scraped.".format(n_items))

if __name__ == "__main__":
    main()