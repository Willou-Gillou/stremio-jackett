#1
import requests
import json  # Assurez-vous d'importer json pour gérer le fichier .txt

from constants import CACHER_URL
from utils.logger import setup_logger

logger = setup_logger(__name__)


def search_cache(query):
    #logger.info(query)
    #query = {'title': '*', 'year': '2024', 'type': 'movie', 'language': 'fr'}
    url = CACHER_URL + "getResult/" + query['type'] + "/"
    response = requests.get(url, json=query)

    # Extraire et analyser le contenu JSON de la réponse
    try:
        cache_results = response.json()
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON response")
        cache_results = []

    num_results = len(cache_results)

    logger.info("\n" + 
    "---------------------------------------------------------------------------------------------------------------" + "\n" +
    "08 - SEARCH_CACHE function launched, sending request to https://stremio-jackett-cacher.elfhosted.com/ " + "\n" +
    "---------------------------------------------------------------------------------------------------------------" + "\n" +
    "******* formating & storing cache URL in $url: "+ str(url)+ "\n" + 
    "******* recall of $query value : "+ str(query)+ "\n" + 
    "******* sending request : requests.get(url, json=query)"+ "\n" +
    "******* number of matches : "+ str(num_results) + "\n" +
#    "******* full response from cacher.elfhosted : \n"+ str(cache_results) + "\n" +
    "******* returning response to main.py \n\n")

    return cache_results
