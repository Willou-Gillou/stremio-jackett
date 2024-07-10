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
    logger.info("\n" + 
    "-------------------------------------------------------------" + "\n" +
    "11 - ITEMS_SORT launched, sorting $items by quality_and_size " + "\n" +
    "-------------------------------------------------------------" + "\n" +
    "******* returning result as $filtered_cached_results to main" + "\n")
    return sorted(items, key=sort_quality_and_size)

def filter_season_episode(items, season, episode, config):
    filtered_items = []
    for item in items:
        if config['language'] == "ru":
            if "S" + str(int(season.replace("S", ""))) + "E" + str(
                    int(episode.replace("E", ""))) not in item['title']:
                if re.search(rf'\bS{re.escape(str(int(season.replace("S", ""))))}\b', item['title']) is None:
                    continue
        if re.search(rf'\b{season}\s?{episode}\b', item['title']) is None:
            if re.search(rf'\b{season}\b', item['title']) is None:
                continue

        filtered_items.append(item)
    return filtered_items

def filter_items(items, item_type=None, config=None, cached=False, season=None, episode=None):
    logger.info("\n" + 
    "----------------------------------------------------------------" + "\n" +
    "10 - FILTER_ITEMS function launched, calling ITEMS_SORT function" + "\n" +
    "----------------------------------------------------------------" + "\n")
    if cached and item_type == "series":
        logger.info("Started filtering series")
        items = filter_season_episode(items, season, episode, config)
    if config['resultsPerQuality'] is not None and int(config['resultsPerQuality']) > 0:
        items = results_per_quality(items, config)
    items = items_sort(items, config)
    return items


def series_file_filter(files, season, episode):
    logger.info("Started filtering series files")
    return files

def results_per_quality(items, config):
    logger.info("Started filtering results per quality (" + str(config['resultsPerQuality']) + " results per quality)")
    filtered_items = []
    quality_count = {}
    for item in items:
        if item['quality'] not in quality_count:
            quality_count[item['quality']] = 1
            filtered_items.append(item)
        else:
            if quality_count[item['quality']] < int(config['resultsPerQuality']):
                quality_count[item['quality']] += 1
                filtered_items.append(item)

    logger.info("Item count changed from " + str(len(items)) + " to " + str(len(filtered_items)))
    return filtered_items