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
    if cached :
        if item_type == "series":
            logger.info("Started filtering series")
            items = filter_season_episode(items, season, episode, config)
        if config['exclusion'] is not None:
            items = quality_exclusion(items, config)
        if config['exclusionKeywords'] is not None and len(config['exclusionKeywords']) > 0:
            logger.info(f"Exclusion keywords: {config['exclusionKeywords']}")
            items = exclusion_keywords(items, config)
        items = items_sort(items, config)
    return items


def series_file_filter(files, season, episode):
    logger.info("Started filtering series files")
    return files

def quality_exclusion(streams, config):
    logger.info("Started filtering quality")
    RIPS = ["HDRIP", "BRRIP", "BDRIP", "WEBRIP", "TVRIP", "VODRIP", "HDRIP"]
    CAMS = ["CAM", "TS", "TC", "R5", "DVDSCR", "HDTV", "PDTV", "DSR", "WORKPRINT", "VHSRIP", "HDCAM"]

    filtered_items = []
    excluded_qualities = [quality.upper() for quality in config['exclusion']]
    rips = "RIPS" in excluded_qualities
    cams = "CAM" in excluded_qualities

    for stream in streams:
        if stream['quality'].upper() not in excluded_qualities:
            detection = detect_quality_spec(stream['title'])
            if detection is not None:
                for item in detection:
                    if rips and item.upper() in RIPS:
                        break
                    if cams and item.upper() in CAMS:
                        break
                else:
                    filtered_items.append(stream)
            else:
                filtered_items.append(stream)
    return filtered_items

def detect_quality_spec(torrent_name):
    quality_patterns = {
        "HDR": r'\b(HDR|HDR10|HDR10PLUS|HDR10PLUS|HDR10PLUS)\b',
        "DTS": r'\b(DTS|DTS-HD)\b',
        "DDP": r'\b(DDP|DDP5.1|DDP7.1)\b',
        "DD": r'\b(DD|DD5.1|DD7.1)\b',
        "SDR": r'\b(SDR|SDRIP)\b',
        "WEBDL": r'\b(WEBDL|WEB-DL|WEB)\b',
        "BLURAY": r'\b(BLURAY|BLU-RAY|BD)\b',
        "DVDRIP": r'\b(DVDRIP|DVDR)\b',
        "CAM": r'\b(CAM|CAMRIP|CAM-RIP)\b',
        "TS": r'\b(TS|TELESYNC|TELESYNC)\b',
        "TC": r'\b(TC|TELECINE|TELECINE)\b',
        "R5": r'\b(R5|R5LINE|R5-LINE)\b',
        "DVDSCR": r'\b(DVDSCR|DVD-SCR)\b',
        "HDTV": r'\b(HDTV|HDTVRIP|HDTV-RIP)\b',
        "PDTV": r'\b(PDTV|PDTVRIP|PDTV-RIP)\b',
        "DSR": r'\b(DSR|DSRRIP|DSR-RIP)\b',
        "WORKPRINT": r'\b(WORKPRINT|WP)\b',
        "VHSRIP": r'\b(VHSRIP|VHS-RIP)\b',
        "VODRIP": r'\b(VODRIP|VOD-RIP)\b',
        "TVRIP": r'\b(TVRIP|TV-RIP)\b',
        "WEBRIP": r'\b(WEBRIP|WEB-RIP)\b',
        "BRRIP": r'\b(BRRIP|BR-RIP)\b',
        "BDRIP": r'\b(BDRIP|BD-RIP)\b',
        "HDCAM": r'\b(HDCAM|HD-CAM)\b',
        "HDRIP": r'\b(HDRIP|HD-RIP)\b',
    }
    qualities = []
    for quality, pattern in quality_patterns.items():
        if re.search(pattern, torrent_name, re.IGNORECASE):
            qualities.append(quality)
    return qualities if qualities else None

def exclusion_keywords(streams, config):
    logger.info("Started filtering exclusion keywords")
    filtered_items = []
    excluded_keywords = [keyword.upper() for keyword in config['exclusionKeywords']]
    for stream in streams:
        for keyword in excluded_keywords:
            if keyword in stream['title'].upper():
                break
        else:
            filtered_items.append(stream)
    return filtered_items