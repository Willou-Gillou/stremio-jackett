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
    return [
        torrent for torrent in torrents 
        if isinstance(torrent, dict) and (torrent['language'] in {language, "multi", "no"})
    ]

def max_size(items, config):
    logger.info("Started filtering size")
    size_limit = int(config['maxSize']) * 1024 ** 3
    return [item for item in items if int(item['size']) <= size_limit]

def exclusion_keywords(streams, config):
    logger.info("Started filtering exclusion keywords")
    excluded_keywords = {keyword.upper() for keyword in config['exclusionKeywords']}
    return [stream for stream in streams if not any(keyword in stream['title'].upper() for keyword in excluded_keywords)]

def quality_exclusion(streams, config):
    logger.info("Started filtering quality")
    RIPS = {"HDRIP", "BRRIP", "BDRIP", "WEBRIP", "TVRIP", "VODRIP", "HDRIP"}
    CAMS = {"CAM", "TS", "TC", "R5", "DVDSCR", "HDTV", "PDTV", "DSR", "WORKPRINT", "VHSRIP", "HDCAM"}

    excluded_qualities = {quality.upper() for quality in config['exclusion']}
    rips = "RIPS" in excluded_qualities
    cams = "CAM" in excluded_qualities

    filtered_items = []
    for stream in streams:
        if stream['quality'].upper() not in excluded_qualities:
            detection = detect_quality_spec(stream['title'])
            if detection:
                for item in detection:
                    if (rips and item.upper() in RIPS) or (cams and item.upper() in CAMS):
                        break
                else:
                    filtered_items.append(stream)
            else:
                filtered_items.append(stream)
    return filtered_items

def results_per_quality(items, config):
    logger.info(f"Started filtering results per quality ({config['resultsPerQuality']} results per quality)")
    quality_count = {}
    filtered_items = []
    for item in items:
        quality = item['quality']
        if quality not in quality_count:
            quality_count[quality] = 1
            filtered_items.append(item)
        elif quality_count[quality] < int(config['resultsPerQuality']):
            quality_count[quality] += 1
            filtered_items.append(item)
    logger.info(f"Item count changed from {len(items)} to {len(filtered_items)}")
    return filtered_items

def sort_quality(item):
    order = {"4k": 0, "1080p": 1, "720p": 2, "480p": 3}
    return order.get(item.get("quality"), float('inf'))

def items_sort(items, config):
    if config['sort'] == "quality":
        return sorted(items, key=sort_quality)
    elif config['sort'] == "sizeasc":
        return sorted(items, key=lambda x: int(x['size']))
    elif config['sort'] == "sizedesc":
        return sorted(items, key=lambda x: int(x['size']), reverse=True)

def filter_season_episode(items, season, episode, config):
    filtered_items = []
    season_number = int(season.replace("S", ""))
    episode_number = int(episode.replace("E", ""))
    season_regex = rf'\bS{season_number:02d}\b'
    episode_regex = rf'\bE{episode_number:02d}\b'

    for item in items:
        if config['language'] == "ru":
            if not re.search(f"S{season_number}E{episode_number}", item['title']) and not re.search(season_regex, item['title']):
                continue
        if not re.search(f"{season}{episode}", item['title']) and not re.search(season_regex, item['title']):
            continue
        filtered_items.append(item)
    return filtered_items

def filter_items(items, item_type=None, config=None, cached=False, season=None, episode=None):
    if config is None or config['language'] is None:
        return items
    
    if cached and item_type == "series":
        items = filter_season_episode(items, season, episode, config)

    logger.info("Started filtering torrents")
    items = filter_language(items, config['language'])

    if int(config['maxSize']) != 0 and item_type == "movie":
        items = max_size(items, config)

    if config['sort'] is not None:
        items = items_sort(items, config)

    if config['exclusionKeywords']:
        logger.info(f"Exclusion keywords: {config['exclusionKeywords']}")
        items = exclusion_keywords(items, config)

    if config['exclusion']:
        items = quality_exclusion(items, config)

    if config['resultsPerQuality'] and int(config['resultsPerQuality']) > 0:
        items = results_per_quality(items, config)

    return items

def series_file_filter(files, season, episode):
    if season is None or episode is None:
        return []

    season = season.lower()
    episode = episode.lower()

    def filter_files(predicate):
        return [file for file in files if predicate(file['path'].lower())]

    # Main filter
    filtered_files = filter_files(lambda path: season + episode in path)
    if filtered_files:
        return filtered_files

    # Secondary fallback filter
    filtered_files = filter_files(lambda path: season in path and episode in path)
    if filtered_files:
        return filtered_files

    # Third fallback filter
    season = season[1:]
    episode = episode[1:]
    filtered_files = filter_files(lambda path: season in path and episode in path and path.index(season) > path.index(episode))
    if filtered_files:
        return filtered_files

    # Last fallback filter
    season = season.lstrip('0')
    episode = episode.lstrip('0')
    filtered_files = filter_files(lambda path: season in path and episode in path and path.index(season) > path.index(episode))
    return filtered_files
