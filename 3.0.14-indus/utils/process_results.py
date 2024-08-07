#1
import concurrent.futures
import base64
import json
import urllib.parse

from utils.get_availability import get_availability_cached
from utils.get_quality import detect_quality, detect_quality_spec
from utils.logger import setup_logger

logger = setup_logger(__name__)

def get_emoji(language):
    emoji_dict = {
        "fr": "🇫🇷",
        "en": "🇬🇧",
        "es": "🇪🇸",
        "de": "🇩🇪",
        "it": "🇮🇹",
        "pt": "🇵🇹",
        "ru": "🇷🇺",
        "in": "🇮🇳",
        "nl": "🇳🇱",
        "multi": "🌍"
    }
    return emoji_dict.get(language, "🇬🇧")


def filter_by_availability(item):
    availability = item["name"][0]
    return 0 if availability == "+" else 1


def process_stream(stream, cached, stream_type, season, episode, config):
    try:
        if "availability" not in stream and not cached:
            return None
    except:
        return None

    if cached:
        if season is None and episode is None:
            availability = get_availability_cached(stream, stream_type, config=config)
        else:
            availability = get_availability_cached(stream, stream_type, season + episode, config=config)
    else:
        availability = stream.get('availability', False)
    if not availability:
        return None
    
    query = {"magnet": stream['magnet'], "type": stream_type}
    if stream_type == "series":
        query['season'] = season
        query['episode'] = episode
    if availability == "AUTH_BLOCKED":
        return {"name": "AUTH_BLOCKED",
                "title": "New connection on AllDebrid.\r\nPlease authorize the connection\r\non your email",
                "url": "#"
        }
    #if availability:
    indexer = stream.get('indexer', 'Cached')
    name = f"+WG-{indexer} + ({detect_quality(stream['title'])} - {detect_quality_spec(stream['title'])})"
    #else:
    #    indexer = stream.get('indexer', 'Cached')
    #    name = f"-{indexer} ({detect_quality(stream['title'])} - {detect_quality_spec(stream['title'])})"
    configb64 = base64.b64encode(json.dumps(config).encode('utf-8')).decode('utf-8').replace('=', '%3D')
    queryb64 = base64.b64encode(json.dumps(query).encode('utf-8')).decode('utf-8').replace('=', '%3D')
    return {
        "name": name,
        "title": f"{stream['title']}\r\n{get_emoji(stream['language'])}   👥 {stream['seeders']}   📂 "
                 f"{round(int(stream['size']) / 1024 / 1024 / 1024, 2)}GB",
        "url": f"{config['addonHost']}/playback/{configb64}/{queryb64}/{urllib.parse.quote_plus(stream['title'].replace(' ', '.'))}"
    }



def process_results(items, cached, stream_type, season=None, episode=None, config=None):
    stream_list = []
    logger.info("PROCESS_RESULTS function launched, calling PROCESS_STREAM function")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(process_stream, items, [cached] * len(items), [stream_type] * len(items),
                               [season] * len(items), [episode] * len(items), [config] * len(items)))
    
    
    if len(results) > 0:
        for result in results:
            if result is not None:
 #               logger.info(f"Appending result: {result}")  # Utilise le logger pour afficher la valeur de result
                stream_list.append(result)

 #   if len(results) > 0:
 #       for result in results:
 #           if result is not None:
 #               stream_list.append(result)

 #   for result in results:
 #       if result is not None:
 #           stream_list.append(result)

    results_log = "\n******* $results :\n" + "\n\n".join([str(result) for result in results])
    logger.info(results_log + "\n")
 #   logger.info(stream_list)

    return sorted(stream_list, key=filter_by_availability)
