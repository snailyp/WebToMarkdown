import hashlib
import os
import re
from pathlib import Path
import base64
from urllib.parse import unquote, urlparse

import requests
from utils.file_io import ensure_directory
from utils.logger import Logger


class ResourceHandler:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.assets_dir = self.output_dir / "assets"
        self.logger = Logger(__name__)

        # Create assets directory if it doesn't exist
        ensure_directory(self.assets_dir)

        # Keep track of downloaded resources
        self.downloaded_resources = {}

        # Configure request session
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "WebToMarkdown Resource Downloader"})

    def download_image(self, image_url):
        """Download image to local assets directory and return relative path"""
        try:
            # Handle base64 encoded images
            if image_url.startswith("data:image/"):
                return self._save_base64_image(image_url)

            # Check if already downloaded
            if image_url in self.downloaded_resources:
                self.logger.debug(f"Using cached version of {image_url}")
                return self.downloaded_resources[image_url]

            # Create a sanitized filename
            parsed_url = urlparse(image_url)
            original_filename = os.path.basename(unquote(parsed_url.path))

            # Handle filenames without extensions
            name, ext = os.path.splitext(original_filename)
            if not ext:
                ext = self._guess_extension(image_url)

            # Create a unique filename using hash if no name available
            if not name:
                name = hashlib.md5(image_url.encode()).hexdigest()[:10]

            # Sanitize filename
            clean_name = re.sub(r"[^\w\-.]", "_", f"{name}{ext}")

            # Handle duplicate filenames
            final_filename = self._get_unique_filename(clean_name)
            local_path = self.assets_dir / final_filename

            # Download the image
            self.logger.info(f"Downloading image: {image_url}")
            response = self.session.get(image_url, timeout=30, stream=True)
            response.raise_for_status()

            # Check content type to verify it's an image
            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                self.logger.warning(
                    f"URL {image_url} is not an image (Content-Type: {content_type})"
                )

            # Save image content
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Store relative path for use in markdown (relative to output root)
            relative_path = f"assets/{final_filename}"
            self.downloaded_resources[image_url] = relative_path

            return relative_path

        except Exception as e:
            self.logger.error(f"Failed to download {image_url}: {e}")
            return image_url  # Return original URL on failure

    def _save_base64_image(self, image_data):
        """Save base64 encoded image to local assets directory and return relative path"""
        try:
            # Extract image type and base64 data
            header, encoded = image_data.split(",", 1)
            file_ext = header.split(";")[0].split("/")[1]
            image_data = base64.b64decode(encoded)

            # Create a unique filename
            name = hashlib.md5(image_data).hexdigest()[:10]
            filename = f"{name}.{file_ext}"
            local_path = self.assets_dir / filename

            # Save image content
            with open(local_path, "wb") as f:
                f.write(image_data)

            # Store relative path for use in markdown (relative to output root)
            relative_path = f"assets/{filename}"
            self.downloaded_resources[image_data] = relative_path

            return relative_path

        except Exception as e:
            self.logger.error(f"Failed to save base64 image: {e}")
            return image_data  # Return original data URL on failure

    def _guess_extension(self, url):
        """Try to guess file extension from URL or default to .jpg"""
        # Check for known image extensions in the URL
        for ext in [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"]:
            if ext in url.lower():
                return ext
        return ".jpg"  # Default extension

    def _get_unique_filename(self, filename):
        """Ensure filename is unique by adding a counter if needed"""
        new_name = filename
        counter = 1

        while (self.assets_dir / new_name).exists():
            name, ext = os.path.splitext(filename)
            new_name = f"{name}_{counter}{ext}"
            counter += 1

        return new_name
