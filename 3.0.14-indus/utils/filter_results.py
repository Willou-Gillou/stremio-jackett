import re
from utils.logger import setup_logger

logger = setup_logger(__name__)

def sort_quality_and_size(item):
    order = {"4k": 0, "1080p": 1, "720p": 2, "480p": 3, "Unknown": 4}
    quality = item.get("quality", "").lower()
    quality_order = order.get(quality, float('inf'))
    try:
        size = int(item.get("size", 0))
    except ValueError:
        size = 0
    return (quality_order, -size)  # sort by quality, then by size in descending order

def items_sort(items, config):
    logger.info("\n" + 
    "-------------------------------------------------------------" + "\n" +
    "11 - ITEMS_SORT launched, sorting $items by quality_and_size " + "\n" +
    "-------------------------------------------------------------" + "\n" +
    "******* returning result as $filtered_cached_results to main" + "\n")
    return sorted(items, key=sort_quality_and_size)

"""
def filter_season_episode(items, season, episode, config):
    logger.info("Started filtering by season and episode")
    return items
"""

#def filter_items(items, item_type=None, config=None, cached=False, season=None, episode=None):
#    logger.info("\n" + 
#    "----------------------------------------------------------------" + "\n" +
#    "10 - FILTER_ITEMS function launched, calling ITEMS_SORT function" + "\n" +
#    "----------------------------------------------------------------" + "\n")
#    if stream_type == "series":
#        filtered_items = [item for item in results if item['type'] == 'series' and item.get('season') == season and item.get('episode') == episode]
#        items = items_sort(filtered_items, config)
 #   else:
        items = items_sort(items, config)
 #   return items
#    items = items_sort(items, config)
#    return items

def filter_items(items, item_type=None, config=None, cached=False, season=None, episode=None):
    logger.info(
        "\n" + 
        "----------------------------------------------------------------" + "\n" +
        "10 - FILTER_ITEMS function launched, calling ITEMS_SORT function" + "\n" +
        "----------------------------------------------------------------" + "\n" +
        "Stream_type:" + str(item_type) + "\n"
    )

    # Filtrer les items si item_type est "series"
    if item_type == "series":
        filtered_items = [item for item in items if item['type'] == 'series' and item.get('season') == season and item.get('episode') == episode]
    else:
        filtered_items = items

    # Appeler items_sort si nécessaire (supposant que items_sort est une fonction existante)
    if config:
        filtered_items = items_sort(filtered_items, config)

    return filtered_items

def series_file_filter(files, season, episode):
    logger.info("Started filtering series files")
    return files