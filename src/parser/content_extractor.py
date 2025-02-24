import re

from bs4 import BeautifulSoup
from bs4.element import Comment
from readability.readability import Document
from utils.logger import Logger


class ContentExtractor:
    logger = Logger(__name__)

    @staticmethod
    def get_main_content(html):
        """Extract main content using readability algorithm"""
        try:
            doc = Document(html)
            return doc.summary()
        except Exception as e:
            ContentExtractor.logger.error(f"Error extracting main content: {e}")
            # Fallback to original HTML if readability fails
            return html

    @staticmethod
    def clean_html(html):
        """Remove scripts, styles, comments and other noise"""
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Remove unwanted tags
            for tag in soup(
                ["script", "style", "noscript", "meta", "iframe", "footer", "nav"]
            ):
                tag.decompose()

            # Remove comments
            for comment in soup.find_all(
                text=lambda text: isinstance(text, Comment)
            ):
                comment.extract()

            # Remove hidden elements
            for tag in soup.find_all(style=re.compile(r"display:\s*none")):
                tag.decompose()

            # Clean attributes from remaining tags
            for tag in soup.find_all(True):
                # Keep only essential attributes
                allowed_attrs = {"href", "src", "alt", "title"}
                attrs = dict(tag.attrs)
                for attr in attrs:
                    if attr not in allowed_attrs:
                        del tag[attr]

            return str(soup)

        except Exception as e:
            ContentExtractor.logger.error(f"Error cleaning HTML: {e}")
            return html

    @staticmethod
    def extract_title(html):
        """Extract page title from HTML"""
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Try to get title from the title tag
            title_tag = soup.find("title")
            if title_tag and title_tag.string:
                return title_tag.string.strip()

            # Fallback to h1 if no title tag
            h1_tag = soup.find("h1")
            if h1_tag and h1_tag.get_text():
                return h1_tag.get_text().strip()

            # Final fallback - look for meta title
            meta_title = soup.find("meta", {"name": "title"}) or soup.find(
                "meta", {"property": "og:title"}
            )
            if meta_title and "content" in meta_title.attrs:
                return meta_title["content"].strip()

            return None

        except Exception as e:
            ContentExtractor.logger.error(f"Error extracting title: {e}")
            return None
