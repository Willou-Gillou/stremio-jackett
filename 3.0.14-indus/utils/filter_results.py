import re
from utils.logger import setup_logger

logger = setup_logger(__name__)

def sort_quality_and_size(item):
    order = {"4k": 0, "1080p": 1, "720p": 2, "480p": 3}
    quality = item.get("quality", "").lower()
    quality_order = order.get(quality, float('inf'))
    try:
        size = int(item.get("size", 0))
    except ValueError:
        size = 0
    return (quality_order, -size)  # sort by quality, then by size in descending order

def items_sort(items, config):
    logger.info("Started sorting items by quality and size")
    return sorted(items, key=sort_quality_and_size)

"""
def filter_season_episode(items, season, episode, config):
    logger.info("Started filtering by season and episode")
    return items
"""

def filter_items(items, item_type=None, config=None, cached=False, season=None, episode=None):
    logger.info("Started filtering torrents in filter_items")
    items = items_sort(items, config)
    return items

"""
def series_file_filter(files, season, episode):
    logger.info("Started filtering series files")
    return files
"""