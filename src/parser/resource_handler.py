import os
from pathlib import Path

import requests
from urllib.parse import urlparse


class ResourceHandler:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir) / "assets"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_image(self, image_url):
        """下载图片到本地并返回相对路径"""
        try:
            response = requests.get(image_url)
            filename = os.path.basename(urlparse(image_url).path)
            local_path = self.output_dir / filename
            with open(local_path, 'wb') as f:
                f.write(response.content)
            return f"./assets/{filename}"
        except Exception as e:
            print(f"Failed to download {image_url}: {e}")
            return image_url  # 失败时保留原URL
