#4
import requests

from utils.logger import setup_logger

logger = setup_logger(__name__)


def replace_weird_characters(string):
    corresp = {
        'ō': 'o', 'ā': 'a', 'ă': 'a', 'ą': 'a', 'ć': 'c', 'č': 'c', 'ç': 'c',
        'ĉ': 'c', 'ċ': 'c', 'ď': 'd', 'đ': 'd', 'è': 'e', 'é': 'e',
        'ê': 'e', 'ë': 'e', 'ē': 'e', 'ĕ': 'e', 'ę': 'e', 'ě': 'e',
        'ĝ': 'g', 'ğ': 'g', 'ġ': 'g', 'ģ': 'g', 'ĥ': 'h', 'î': 'i',
        'ï': 'i', 'ì': 'i', 'í': 'i', 'ī': 'i', 'ĩ': 'i', 'ĭ': 'i',
        'ı': 'i', 'ĵ': 'j', 'ķ': 'k', 'ĺ': 'l', 'ļ': 'l', 'ł': 'l',
        'ń': 'n', 'ň': 'n', 'ñ': 'n', 'ņ': 'n', 'ŉ': 'n', 'ó': 'o',
        'ô': 'o', 'õ': 'o', 'ö': 'o', 'ø': 'o', 'ō': 'o', 'ő': 'o',
        'œ': 'oe', 'ŕ': 'r', 'ř': 'r', 'ŗ': 'r', 'š': 's', 'ş': 's',
        'ś': 's', 'ș': 's', 'ß': 'ss', 'ť': 't', 'ţ': 't', 'ū': 'u',
        'ŭ': 'u', 'ũ': 'u', 'û': 'u', 'ü': 'u', 'ù': 'u', 'ú': 'u',
        'ų': 'u', 'ű': 'u', 'ŵ': 'w', 'ý': 'y', 'ÿ': 'y', 'ŷ': 'y',
        'ž': 'z', 'ż': 'z', 'ź': 'z', 'æ': 'ae', 'ǎ': 'a', 'ǧ': 'g',
        'ə': 'e', 'ƒ': 'f', 'ǐ': 'i', 'ǒ': 'o', 'ǔ': 'u', 'ǚ': 'u',
        'ǜ': 'u', 'ǹ': 'n', 'ǻ': 'a', 'ǽ': 'ae', 'ǿ': 'o',
    }

    for weird_char in corresp:
        string = string.replace(weird_char, corresp[weird_char])

    return string



def get_name(id, type, config):
    
    if type == "movie":
    full_id = id.split(":")
    url = f"https://api.themoviedb.org/3/find/{full_id[0]}?api_key={config['tmdbApi']}&external_source=imdb_id&language={config['language']}"
    response = requests.get(url)
    data = response.json()
    result = {
        "title": replace_weird_characters(data["movie_results"][0]["title"]),
        "year": data["movie_results"][0]["release_date"][:4],
        "type": "movie",
        "language": config['language']
    }
    
    # Logging each key-value pair in data
    data_log = ""
    for key, value in data.items():
        data_log += str(key) + ": " + str(value) + "\n"
    
    logger.info("\n" + 
        "----------------------------------------------------------------------" + "\n" +
        "05 - GET_NAME function launched, sending request to TheMovieDataBase API :\n" +
        "----------------------------------------------------------------------" + "\n" +
        "******* stream_type: " + type + "\n" +
        "******* stream_id: " + id + "\n" +
        "******* language from config: " + str(config['language']) + "\n" +
        "******* response from TheMovieDataBase : \n" + data_log +
        
        "-------------------------------------------------------------------------" + "\n" +
        "06 - Extracting only Title, year, type and Language values  :\n" +
        "-------------------------------------------------------------------------" + "\n" +
        "******* result : " + str(result) + "\n" +
        "******* returning result as $name in main.py \n\n") 
    return result
    
    else:
        full_id = id.split(":")
        url = f"https://api.themoviedb.org/3/find/{full_id[0]}?api_key={config['tmdbApi']}&external_source=imdb_id&language={config['language']}"
        response = requests.get(url)
        data = response.json()
        result = {
            "title": replace_weird_characters(data["tv_results"][0]["name"]),
            "season": "S{:02d}".format(int(full_id[1])),
            "episode": "E{:02d}".format(int(full_id[2])),
            "type": "series",
            "language": config['language']
        }
        #logger.info("\n" + 
            #"----------------------------------------------------------------------" + "\n" +
            #"05 - GET_NAME function launched, sending request to TheMovieDataBase API :\n" +
            #"----------------------------------------------------------------------" + "\n" +
            #"******* stream_type: " + type + "\n" +
            #"******* stream_id: " + id + "\n" +
            #"******* language from config: " + str(config['language']) + "\n" +
            #"******* response from TheMovieDataBase : " + str(data) + "\n\n" +
        logger.info("\n" + 
            "----------------------------------------------------------------------" + "\n" +
            "05 - GET_NAME function launched, sending request to TheMovieDataBase API :\n" +
            "----------------------------------------------------------------------" + "\n" +
            f"******* stream_type: {type}\n" +
            f"******* stream_id: {id}\n" +
            f"******* language from config: {config['language']}\n" +
            "******* response from TheMovieDataBase :\n" +
            f"{json.dumps(data, indent=2)}\n\n" +   
            
            "-------------------------------------------------------------------------" + "\n" +
            "06 - Extracting only Title, year, type and Language values  :\n" +
            "-------------------------------------------------------------------------" + "\n" +
            "******* result : " + str(result) + "\n" +
            "******* returning result as $name in main.py \n\n") 
        return result
