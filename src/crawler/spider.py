import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from crawler.robots_parser import RobotsParser
from utils.logger import Logger


class WebSpider:
    def __init__(self, base_url, max_depth=5, delay=1, user_agent=None):
        self.base_url = base_url
        self.max_depth = max_depth
        self.delay = delay  # Time to wait between requests in seconds
        self.visited = set()
        self.to_visit = [(base_url, 0)]
        self.logger = Logger(__name__)

        # Set up user agent for requests
        self.user_agent = user_agent or "WebToMarkdown Bot"
        self.headers = {"User-Agent": self.user_agent}

        # Domain for filtering external links
        self.domain = urlparse(base_url).netloc

        # Set up robots.txt parser
        self.robots_parser = RobotsParser(base_url, self.user_agent)

        # File extensions to skip
        self.skip_extensions = {
            ".pdf",
            ".zip",
            ".rar",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",
            ".exe",
        }

    def _is_valid_url(self, url):
        """Filter out invalid URLs, external links, and already visited pages"""
        try:
            parsed = urlparse(url)

            # Check if URL is valid
            if not parsed.scheme or not parsed.netloc:
                return False

            # Check if URL is already visited
            if url in self.visited:
                return False

            # Check if URL is from the same domain
            if parsed.netloc != self.domain:
                return False

            # Check file extension
            path = parsed.path.lower()
            if any(path.endswith(ext) for ext in self.skip_extensions):
                return False

            # Check robots.txt rules
            if not self.robots_parser.can_fetch(url):
                self.logger.debug(f"Skipping {url} (blocked by robots.txt)")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating URL {url}: {e}")
            return False

    def normalize_url(self, base, url):
        """Convert a relative URL to an absolute URL"""
        return urljoin(base, url)

    def _extract_links(self, soup, current_url):
        """Extract and normalize all links from the page"""
        links = []
        for link in soup.find_all("a", href=True):
            try:
                href = link["href"].strip()
                # Skip empty links and javascript links
                if not href or href.startswith("javascript:") or href.startswith("#"):
                    continue

                # Normalize URL
                full_url = self.normalize_url(current_url, href)

                # Remove fragments and normalize
                full_url = re.sub(r"#.*$", "", full_url)

                if self._is_valid_url(full_url):
                    links.append(full_url)

            except Exception as e:
                self.logger.error(f"Error extracting link {link}: {e}")

        return links

    def crawl(self):
        """Crawl pages up to the specified depth and yield URL and HTML content"""
        self.logger.info(
            f"Starting crawl of {self.base_url} with max depth {self.max_depth}"
        )

        while self.to_visit:
            url, depth = self.to_visit.pop(0)

            if url in self.visited:
                continue

            if depth > self.max_depth:
                continue

            try:
                # Respect crawl delay
                time.sleep(self.delay)

                self.logger.info(f"Crawling {url} (depth {depth})")
                response = requests.get(url, headers=self.headers, timeout=30)

                # Skip non-HTML responses
                if "text/html" not in response.headers.get("Content-Type", ""):
                    self.logger.debug(f"Skipping non-HTML content: {url}")
                    self.visited.add(url)
                    continue

                # Skip error status codes
                if response.status_code != 200:
                    self.logger.warning(
                        f"Got status code {response.status_code} for {url}"
                    )
                    self.visited.add(url)
                    continue

                soup = BeautifulSoup(response.content.decode('utf-8'), "html.parser")
                self.visited.add(url)

                # Extract links for future crawling
                links = self._extract_links(soup, url)
                for link in links:
                    if (
                        link not in self.visited
                        and (link, depth + 1) not in self.to_visit
                    ):
                        self.to_visit.append((link, depth + 1))

                yield url, response.content.decode("utf-8")

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request error crawling {url}: {e}")
                self.visited.add(url)  # Mark as visited to avoid retrying
            except Exception as e:
                self.logger.error(f"Error crawling {url}: {e}")
                self.visited.add(url)
