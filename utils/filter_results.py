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
    filtered_torrents = []
    for torrent in torrents:
        if type(torrent) is str:
            logger.error(f"Torrent is a string: {torrent}")
            continue
        if not torrent['language']:
            continue
        if torrent['language'] == language:
            filtered_torrents.append(torrent)
        if torrent['language'] == "multi":
            filtered_torrents.append(torrent)
        if torrent['language'] == "no":
            filtered_torrents.append(torrent)
    return filtered_torrents

def max_size(items, config):
    logger.info("Started filtering size")
    return items

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

def results_per_quality(items, config):
    logger.info(f"Started filtering results per quality ({config['resultsPerQuality']} results per quality)")
    return items

def sort_quality(item):
    order = {"4k": 0, "1080p": 1, "720p": 2, "480p": 3}
    return order.get(item.get("quality"), float('inf'))

def items_sort(items, config):
    logger.info(f"Started sorting items by quality")
    return sorted(items, key=sort_quality)

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
