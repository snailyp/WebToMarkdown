from bs4 import BeautifulSoup
from readability import Document


class ContentExtractor:
    @staticmethod
    def get_main_content(html):
        """使用readability提取正文"""
        doc = Document(html)
        return doc.summary()

    @staticmethod
    def clean_html(html):
        """移除脚本/样式/注释等噪音"""
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup(['script', 'style', 'noscript', 'meta', 'comment']):
            tag.decompose()
        return str(soup)
