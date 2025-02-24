# WebToMarkdown 🌐 ➡️ 📝

一个强大的网页转Markdown工具，让您轻松实现文档站点的完全本地化！✨

本工具可以将在线文档站点完整地转换为Markdown文件，包括图片等资源文件的本地化处理，使您能够在完全离线的环境下浏览和管理文档。

## 功能特点 🎯

- 📱 支持文档站点完全本地化
- 🕷️ 智能网页爬取
- 📄 HTML到Markdown的精准转换
- 🖼️ 资源文件自动处理
- 🤖 支持robots.txt解析
- 📁 灵活的文件IO操作
- 📝 详细的日志记录

## 项目结构 📂

```plaintext
WebToMarkdown/
├── config/           # 配置文件目录
├── docs/            # 文档目录
├── src/             # 源代码目录
│   ├── crawler/     # 爬虫模块
│   ├── parser/      # 解析器模块
│   └── utils/       # 工具类模块
└── tests/           # 测试目录
```

## 安装 🔧

```bash
pip install -r requirements.txt
```

## 使用方法 📖

1. 配置文件设置

在 `config/default.yaml` 中配置相关参数：

```yaml
target_url: "https://example.com"
output_dir: "./output"
max_depth: 3
delay: 1
user_agent: "WebToMarkdown Bot"
download_images: true
ignore_links: false
bypass_tables: false
```

2. 运行服务

在命令行中运行：

```bash
python src/web_to_markdown.py
```

这将开始网页爬取和转换过程。转换后的 Markdown 文件将保存在配置文件中指定的输出目录中。

## 主要模块说明 🔍

### Crawler 模块 🕷️

- `robots_parser.py`: 解析网站的robots.txt文件
- `spider.py`: 实现网页爬取功能

### Parser 模块 📝

- `content_extractor.py`: 提取网页主要内容
- `html_to_md.py`: HTML转Markdown核心转换器
- `resource_handler.py`: 处理图片等资源文件

### Utils 模块 🛠️

- `file_io.py`: 文件读写操作
- `logger.py`: 日志记录功能

## 贡献指南 🤝

欢迎提交Issue和Pull Request来帮助改进项目！

## 许可证 📄

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解更多详情
