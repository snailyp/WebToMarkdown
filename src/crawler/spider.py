import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup


class WebSpider:
    def __init__(self, base_url, max_depth=5):
        self.base_url = base_url
        self.max_depth = max_depth
        self.visited = set()
        self.to_visit = [(base_url, 0)]

    def _is_valid_url(self, url):
        """过滤非本站和非HTTP链接"""
        return url.startswith(self.base_url) and url not in self.visited

    def crawl(self):
        """递归爬取所有页面"""
        while self.to_visit:
            url, depth = self.to_visit.pop(0)
            if depth > self.max_depth:
                continue

            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                self.visited.add(url)

                # 提取页面内的所有链接
                for link in soup.find_all('a', href=True):
                    full_url = urljoin(url, link['href'])
                    if self._is_valid_url(full_url):
                        self.to_visit.append((full_url, depth + 1))

                yield url, response.text

            except Exception as e:
                print(f"Error crawling {url}: {e}")
