import os
from pathlib import Path
import shutil
import json
from src.utils.logger import get_logger


logger = get_logger(__name__)


def ensure_directory(path):
    """Create directory if it doesn't exist"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return False


def write_file(path, content, mode='w', encoding='utf-8'):
    """Write content to file with error handling"""
    try:
        with open(path, mode, encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error writing to {path}: {e}")
        return False


def read_file(path, mode='r', encoding='utf-8'):
    """Read content from file with error handling"""
    try:
        with open(path, mode, encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading {path}: {e}")
        return None


def save_json(path, data, indent=2):
    """Save data as JSON file"""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {path}: {e}")
        return False


def load_json(path):
    """Load data from JSON file"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {path}: {e}")
        return None


def copy_file(src, dest):
    """Copy file with error handling"""
    try:
        shutil.copy2(src, dest)
        return True
    except Exception as e:
        logger.error(f"Error copying {src} to {dest}: {e}")
        return False


def get_file_extension(path):
    """Get file extension from path"""
    return os.path.splitext(path)[1].lower()
