from src.config_loader import ConfigLoader
from src.crawler.spider import WebSpider
from src.parser.content_extractor import ContentExtractor
from src.parser.html_to_md import HTML2Markdown
from src.parser.resource_handler import ResourceHandler
from pathlib import Path


class WebToMarkdown:
    def __init__(self, config_path="config/default.yaml"):
        self.config = ConfigLoader(config_path)
        self.spider = WebSpider(
            self.config.get('target_url'),
            self.config.get('max_depth', 5)
        )
        self.md_converter = HTML2Markdown()
        self.res_handler = ResourceHandler(self.config.get('output_dir'))

    def run(self):
        for url, html in self.spider.crawl():
            # 内容清洗与转换
            cleaned_html = ContentExtractor.clean_html(html)
            main_content = ContentExtractor.get_main_content(cleaned_html)
            markdown = self.md_converter.convert(main_content)

            # 处理图片资源
            final_md = self._replace_image_urls(markdown)

            # 保存文件
            self._save_markdown(url, final_md)

    def _replace_image_urls(self, markdown):
        """替换Markdown中的图片URL为本地路径"""
        # 实现正则匹配图片语法并调用download_image
        processed_markdown = self.res_handler.download_image(markdown)
        return processed_markdown

    def _save_markdown(self, url, content):
        """根据URL生成文件路径"""
        path = url.replace(self.config.get('target_url'), '').strip('/')
        output_path = Path(self.config.get('output_dir')) / f"{path}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
