from config_loader import ConfigLoader
from crawler.spider import WebSpider
from parser.content_extractor import ContentExtractor
from parser.html_to_md import HTML2Markdown
from parser.resource_handler import ResourceHandler
from utils.logger import Logger
from pathlib import Path
import re


class WebToMarkdown:
    def __init__(self, config_path="config/default.yaml"):
        self.config = ConfigLoader(config_path)
        self.logger = Logger(__name__)
        self.spider = WebSpider(
            self.config.get('target_url'),
            self.config.get('max_depth', 5),
            self.config.get('delay', 1),
            self.config.get('user_agent')
        )
        self.md_converter = HTML2Markdown(
            self.config.get('ignore_links', False),
            self.config.get('bypass_tables', False)
        )
        self.res_handler = ResourceHandler(self.config.get('output_dir'))

    def run(self):
        """Main execution method that crawls, processes, and saves content"""
        self.logger.info(f"Starting crawl of {self.config.get('target_url')}")
        
        for url, html in self.spider.crawl():
            try:
                self.logger.info(f"Processing {url}")
                
                # Clean and convert content
                cleaned_html = ContentExtractor.clean_html(html)
                main_content = ContentExtractor.get_main_content(cleaned_html)
                
                # Extract title for the markdown file
                title = ContentExtractor.extract_title(cleaned_html)
                
                # Convert to markdown
                markdown = self.md_converter.convert(main_content)
                
                # Add title to markdown if available
                if title:
                    markdown = f"# {title}\n\n{markdown}"
                
                # Handle images and other resources
                final_md = self._replace_image_urls(markdown, url)
                
                # Save the processed markdown
                output_path = self._save_markdown(url, final_md)
                self.logger.info(f"Saved to {output_path}")
                
            except Exception as e:
                self.logger.error(f"Error processing {url}: {e}")

    def _replace_image_urls(self, markdown, base_url):
        """Replace image URLs in markdown with local paths"""
        # Regular expression to find markdown image syntax
        img_pattern = r'!\[(.*?)\]\((.*?)\)'
        
        def replace_img(match):
            alt_text = match.group(1)
            img_url = match.group(2)
            
            # Convert relative URLs to absolute
            if not img_url.startswith(('http://', 'https://')):
                img_url = self.spider.normalize_url(base_url, img_url)
                
            # Download the image and get local path (relative to output root)
            asset_path = self.res_handler.download_image(img_url)
            
            # Calculate relative path based on URL depth
            url_path = base_url[len(self.config.get('target_url')):].strip('/')
            depth = len(url_path.split('/')) - 1 if url_path else 0
            prefix = '../' * depth if depth > 0 else './'
            
            # Construct final path
            local_path = f"{prefix}{asset_path}"
            
            # Return updated markdown image syntax
            return f'![{alt_text}]({local_path})'
        
        return re.sub(img_pattern, replace_img, markdown)

    def _save_markdown(self, url, content):
        """Generate file path based on URL and save content"""
        try:
            base_url = self.config.get('target_url')
            # Create a clean filename from URL
            if url.startswith(base_url):
                path = url[len(base_url):].strip('/')
            else:
                path = url.replace('://', '_').replace('/', '_')
                
            # Handle empty path (homepage)
            if not path:
                path = "index"
                
            output_dir = Path(self.config.get('output_dir'))
            output_path = output_dir / f"{path}.md"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error saving markdown for {url}: {e}")
            # Fallback to a safe filename
            output_path = Path(self.config.get('output_dir')) / f"page_{hash(url) % 10000}.md"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return output_path


if __name__ == '__main__':
    WebToMarkdown().run()
