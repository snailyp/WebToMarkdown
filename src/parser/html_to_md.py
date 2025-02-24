import html2text


class HTML2Markdown:
    def __init__(self):
        self.converter = html2text.HTML2Text()
        self.converter.ignore_links = False
        self.converter.bypass_tables = False

    def convert(self, html):
        """核心转换方法"""
        return self.converter.handle(html)
