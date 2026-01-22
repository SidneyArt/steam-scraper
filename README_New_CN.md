# Steam Scraper 使用指南

这是一个用于抓取 [Steam 游戏商店](https://store.steampowered.com/) 产品信息和用户评论的爬虫工具。

本项目已经针对 Windows 环境进行了优化，支持通过 Miniconda/Anaconda 进行一键式部署和运行。

## 1. 准备工作

在开始之前，请确保你的电脑上已经安装了 [Miniconda](https://docs.conda.io/en/latest/miniconda.html) 或 Anaconda。

## 2. 环境安装 (只需一次)

双击运行项目根目录下的脚本：
👉 **`install_env.bat`**

该脚本会自动执行以下操作：
1. 创建名为 `steam-scraper` 的 Python 虚拟环境。
2. 安装 Scrapy 爬虫框架及所有必要的依赖库。
3. 自动修复 Windows 下可能出现的编译错误。

*安装过程中如果提示确认，请输入 `y` 并回车。等待脚本显示 "Setup Complete!" 即表示安装成功。*

## 3. 运行爬虫

### 🎮 爬取游戏列表
双击运行：
👉 **`run_products.bat`**

*   **功能**：抓取 Steam 商店的所有游戏基本信息（价格、评分、标签、发行日期等）。
*   **输出**：结果会实时保存到 `output/products_all.jl`。
*   **注意**：这是一个耗时操作，因为它会遍历整个 Steam 目录。你可以随时按 `Ctrl+C` 停止，下次运行时它会尝试断点续传。

### 💬 爬取游戏评论
双击运行：
👉 **`run_reviews.bat`**

*   **功能**：抓取指定游戏的玩家评论。
*   **配置**：默认情况下，它会抓取 `steam/test_urls.txt` 中配置的游戏链接。如果你想抓取特定游戏，请修改该文件，或者修改 `run_reviews.bat` 中的启动参数。

## 4. 查看结果 (转换数据)

爬虫默认生成的 `.jl` (JSON Lines) 文件适合程序读取，但不方便人类阅读。我们提供了一个转换工具，可以将其转换为 Excel 表格或格式化的 JSON。

双击运行：
👉 **`convert_results.bat`**

该脚本会自动读取 `output/products_all.jl`，并在同一目录下生成：
1.  📄 **`products_all.csv`**：**推荐！** 可以直接用 **Excel** 打开，方便筛选、排序和分析。
2.  📝 **`products_all_pretty.json`**：格式化后的 JSON 文件，结构清晰，适合查看详细数据结构。

## 5. 输出文件说明

所有结果都保存在 `output` 文件夹中：

| 文件名 | 说明 |
| :--- | :--- |
| `products_all.jl` | 原始爬虫数据（每行一条 JSON）。 |
| `products_all.csv` | **Excel 表格文件**，包含游戏名、价格、评分等列。 |
| `products_all_pretty.json` | 易读的 JSON 文件。 |
| `products_all.log` | 爬虫运行日志，用于排查错误。 |

## 常见问题

**Q: 运行脚本时出现闪退？**
A: 请检查是否已经正确安装了 Miniconda，并且路径设置正确。脚本默认假设 Miniconda 安装在 `C:\ProgramData\miniconda3`。如果你的安装路径不同，请右键编辑 `.bat` 文件，修改其中的路径。

**Q: 爬取速度太慢？**
A: 为了防止被 Steam 封禁 IP，爬虫默认设置了一定的延迟。请勿随意加快速度，否则可能导致无法访问 Steam 商店。
