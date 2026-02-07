# Steam Scraper (Steam 爬虫)

本仓库包含用于从 [Steam 游戏商店](https://steampowered.com) **抓取产品信息** 和 **所有用户提交的评论** 的 [Scrapy](https://github.com/scrapy/scrapy) 爬虫。
此外还包含一些用于更轻松管理和部署爬虫的脚本。

本仓库包含的代码是配合发布在 [Scrapinghub 博客](https://blog.scrapinghub.com/2017/07/07/scraping-the-steam-game-store-with-scrapy/) 和 [Intoli 博客](https://intoli.com/blog/steam-scraper/) 上的文章 *Scraping the Steam Game Store* 编写的。

## 安装

克隆仓库：
```bash
git clone git@github.com:prncc/steam-scraper.git
```

启动并激活 Python 3.6+ 虚拟环境：
```bash
cd steam-scraper
virtualenv -p python3.6 env
. env/bin/activate
```

安装 Python 依赖：
```bash
pip install -r requirements.txt
```

顺便提一下，在 macOS 上你可以通过 [homebrew](https://brew.sh) 安装 Python 3.6：
```bash
 brew install python3
```

在 Ubuntu 上你可以参考 [askubuntu.com 上的说明](https://askubuntu.com/questions/865554/how-do-i-install-python-3-6-using-apt-get)。

## 抓取产品

`ProductSpider` 的目的是在 [Steam 产品列表](http://store.steampowered.com/search/?sort_by=Released_DESC) 上发现产品页面并从中提取有用的元数据。
这个爬虫的一个巧妙功能是它会自动通过 Steam 的年龄验证检查点。

你可以通过以下命令启动这个耗时数小时的抓取任务：
```bash
scrapy crawl products -o output/products_all.jl --logfile=output/products_all.log --loglevel=INFO -s JOBDIR=output/products_all_job -s HTTPCACHE_ENABLED=False
```

完成后，你应该会在 `output/products_all.jl` 中得到 Steam 上所有游戏的元数据。
输出示例如下：
```python
{
  'app_name': 'Cold Fear™',
  'developer': 'Darkworks',
  'early_access': False,
  'genres': ['Action'],
  'id': '15270',
  'metascore': 66,
  'n_reviews': 172,
  'price': 9.99,
  'publisher': 'Ubisoft',
  'release_date': '2005-03-28',
  'reviews_url': 'http://steamcommunity.com/app/15270/reviews/?browsefilter=mostrecent&p=1',
  'sentiment': 'Very Positive',
  'specs': ['Single-player'],
  'tags': ['Horror', 'Action', 'Survival Horror', 'Zombies', 'Third Person', 'Third-Person Shooter'],
  'title': 'Cold Fear™',
  'url': 'http://store.steampowered.com/app/15270/Cold_Fear/'
 }
```

## 提取评论

`ReviewSpider` 的目的是从 [Steam 社区门户](http://steamcommunity.com/) 抓取特定产品的所有用户提交的评论。
默认情况下，它从 `test_urls` 参数中列出的 URL 开始：
```python
class ReviewSpider(scrapy.Spider):
    name = 'reviews'
    test_urls = [
        "http://steamcommunity.com/app/316790/reviews/?browsefilter=mostrecent&p=1",  # Grim Fandango
        "http://steamcommunity.com/app/207610/reviews/?browsefilter=mostrecent&p=1",  # The Walking Dead
        "http://steamcommunity.com/app/414700/reviews/?browsefilter=mostrecent&p=1"   # Outlast 2
    ]
```

它也可以通过 `url_file` 命令行参数读取包含 URL 的文本文件（如下所示）：
```
http://steamcommunity.com/app/316790/reviews/?browsefilter=mostrecent&p=1
http://steamcommunity.com/app/207610/reviews/?browsefilter=mostrecent&p=1
http://steamcommunity.com/app/414700/reviews/?browsefilter=mostrecent&p=1
```

命令如下：
```bash
scrapy crawl reviews -o reviews.jl -a url_file=url_file.txt -s JOBDIR=output/reviews
```

输出示例：
```python
{
  'date': '2017-06-04',
  'early_access': False,
  'found_funny': 5,
  'found_helpful': 0,
  'found_unhelpful': 1,
  'hours': 9.8,
  'page': 3,
  'page_order': 7,
  'product_id': '414700',
  'products': 179,
  'recommended': True,
  'text': '3 spooky 5 me',
  'user_id': '76561198116659822',
  'username': 'Fowler'
}
```

如果你想获取所有产品的所有评论，`split_review_urls.py` 将从 `products_all.jl` 中移除重复条目，并将 `review_url` 分散到几个文本文件中。
这提供了一种方便的方法，可以将抓取任务拆分为可管理的小块。
鉴于 Steam 宽松的速率限制，整个任务需要几天时间。

## 部署到远程服务器

本节简要说明如何在一个或多个 t1.micro AWS 实例上运行抓取。

首先，创建一个 Ubuntu 16.04 t1.micro 实例，并在你的 `~/.ssh/config` 文件中将其命名为 `scrapy-runner-01`：
```
Host scrapy-runner-01
     User ubuntu
     HostName <server's IP>
     IdentityFile ~/.ssh/id_rsa
```
本仓库中包含的 `scrapydee.sh` 辅助脚本需要这种形式的主机名。
确保你可以通过 `ssh scrappy-runner-01` 连接。

### 远程服务器设置

实际运行抓取的工具是运行在远程服务器上的 [scrapyd](http://scrapyd.readthedocs.io/en/stable/)。
要进行设置，首先安装 Python 3.6：
```bash
sudo add-apt-repository ppa:jonathonf/python-3.6
sudo apt update
sudo apt install python3.6 python3.6-dev virtualenv python-pip
```

然后，在远程服务器上专用的 `run` 目录中安装 scrapyd 和其余依赖项：
```bash
mkdir run && cd run
virtualenv -p python3.6 env
. env/bin/activate
pip install scrapy scrapyd botocore smart_getenv  
```

你可以通过以下命令从虚拟环境运行 `scrapyd`：
```bash
scrapyd --logfile /home/ubuntu/run/scrapyd.log &
```
如果断开与服务器的连接，你可能希望使用类似 [screen](https://www.gnu.org/software/screen/) 的工具来保持进程存活。

### 控制任务

你可以使用简单的 [HTTP JSON API](http://scrapyd.readthedocs.io/en/stable/index.html) 向远程机器上运行的 scrapyd 进程发送命令。
首先，为本项目创建一个 egg 包：
```bash
python setup.py bdist_egg
```

通过以下命令将 egg 包和你的评论 URL 文件复制到 `scrapy-runner-01`：
```bash
scp output/review_urls_01.txt scrapy-runner-01:/home/ubuntu/run/
scp dist/steam_scraper-1.0-py3.6.egg scrapy-runner-01:/home/ubuntu/run
```

并通过以下命令将其添加到 scrapyd 的任务目录：
```bash
ssh -f scrapy-runner-01 'cd /home/ubuntu/run && curl http://localhost:6800/addversion.json -F project=steam -F egg=@steam_scraper-1.0-py3.6.egg'
```
向来自你家庭 IP 的 TCP 流量开放 6800 端口，将允许你不通过 SSH 就能发出此命令。
如果此命令不起作用，你可能需要编辑 `scrapyd.conf`，在 `[scrapyd]` 部分包含：
```
bind_address = 0.0.0.0
```
顺便提一下，有一个 [scrapyd-client](https://github.com/scrapy/scrapyd-client) 项目用于将 egg 包部署到配备 scrapyd 的服务器。
我选择不使用它，因为它不知道 `~/.ssh/config` 中已经设置好的服务器，因此需要重复配置。

最后，用类似以下的命令启动任务：
```bash
ssh scrapy-runner-01 'curl http://localhost:6800/schedule.json -d project=steam -d spider=reviews -d url_file="/home/ubuntu/run/review_urls_01.txt" -d jobid=part_01 -d setting=FEED_URI="s3://'$STEAM_S3_BUCKET'/%(name)s/part_01/%(time)s.jl" -d setting=AWS_ACCESS_KEY_ID='$AWS_ACCESS_KEY_ID' -d setting=AWS_SECRET_ACCESS_KEY='$AWS_SECRET_ACCESS_KEY' -d setting=LOG_LEVEL=INFO'
```
此命令假设你已经设置了一个 S3 存储桶以及 `AWS_ACCESS_KEY_ID` 和 `AWS_SECRET_ACCESS_KEY` 环境变量。
不过，将其自定义为非 S3 输出应该很容易。

本仓库 `scripts` 目录中包含的 `scrapydee.sh` 辅助脚本提供了一些快捷方式，用于向主机名为 `scrapy-runner-01` 形式的配备 scrapyd 的服务器发送命令。
例如，命令：
```bash
./scripts/scrapydee.sh status 1
# Executing status()...
# On server(s): 1.
```
将在 `scrapy-runner-01` 上运行 `scrapydee.sh` 中定义的 `status()` 函数。
更多命令示例请参阅该文件。
你也可以在多台服务器上运行每个包含的命令：
首先，更改 `scrapydee.sh` 中的 `all()` 函数以匹配你配置的服务器数量。
然后，发出如下命令：
```bash
./scripts/scrapydee.sh status all
```
输出有点乱，但这是运行此任务的一种快速简便的方法。
