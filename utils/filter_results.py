import re
from utils.logger import setup_logger

logger = setup_logger(__name__)

def detect_quality_spec(torrent_name):
    quality_patterns = {
        "HDR": r'\b(HDR|HDR10|HDR10PLUS)\b',
        "DTS": r'\b(DTS|DTS-HD)\b',
        "DDP": r'\b(DDP|DDP5.1|DDP7.1)\b',
        "DD": r'\b(DD|DD5.1|DD7.1)\b',
        "SDR": r'\b(SDR|SDRIP)\b',
        "WEBDL": r'\b(WEBDL|WEB-DL|WEB)\b',
        "BLURAY": r'\b(BLURAY|BLU-RAY|BD)\b',
        "DVDRIP": r'\b(DVDRIP|DVDR)\b',
        "CAM": r'\b(CAM|CAMRIP|CAM-RIP)\b',
        "TS": r'\b(TS|TELESYNC)\b',
        "TC": r'\b(TC|TELECINE)\b',
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

def filter_language(torrents, language):
    logger.info(f"Filtering torrents by language: {language}")
    return torrents

def max_size(items, config):
    logger.info("Started filtering size")
    return items

def exclusion_keywords(streams, config):
    logger.info("Started filtering exclusion keywords")
    filtered_items = []
    excluded_keywords = [keyword.upper() for keyword in config['exclusionKeywords']]
    for stream in streams:
        title = stream.get('title', '').upper()
        if any(keyword in title for keyword in excluded_keywords):
            continue
        filtered_items.append(stream)
    return filtered_items

def quality_exclusion(streams, config):
    logger.info("Started filtering quality")
    return streams

def results_per_quality(items, config):
    logger.info(f"Started filtering results per quality ({config['resultsPerQuality']} results per quality)")
    return items

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

def filter_season_episode(items, season, episode, config):
    logger.info("Started filtering by season and episode")
    return items

def filter_items(items, item_type=None, config=None, cached=False, season=None, episode=None):
    logger.info("Started filtering torrents")
    items = items_sort(items, config)
    return items

def series_file_filter(files, season, episode):
    logger.info("Started filtering series files")
    return files
