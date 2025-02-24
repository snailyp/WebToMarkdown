from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

from utils.logger import Logger


class RobotsParser:
    def __init__(self, base_url, user_agent):
        self.logger = Logger(__name__)
        self.user_agent = user_agent
        self.rp = RobotFileParser()

        try:
            # Construct robots.txt URL
            parsed = urlparse(base_url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

            self.logger.info(f"Fetching robots.txt from {robots_url}")
            response = requests.get(robots_url, timeout=10)

            if response.status_code == 200:
                self.rp.parse(response.text.splitlines())
                self.logger.info("Successfully parsed robots.txt")
            else:
                self.logger.warning(
                    f"Could not fetch robots.txt ({response.status_code}), assuming all URLs allowed"
                )
                # If robots.txt doesn't exist, allow all
                self.rp.allow_all = True

        except Exception as e:
            self.logger.error(f"Error processing robots.txt: {e}")
            # Be permissive on error
            self.rp.allow_all = True

    def can_fetch(self, url):
        """Check if URL is allowed by robots.txt"""
        try:
            return self.rp.can_fetch(self.user_agent, url)
        except Exception as e:
            self.logger.error(f"Error checking robots.txt rules for {url}: {e}")
            return True  # Allow if there's an error checking
