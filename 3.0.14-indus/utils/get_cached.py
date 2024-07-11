#1
import requests
import json  # Assurez-vous d'importer json pour gérer le fichier .txt

from constants import CACHER_URL
from utils.logger import setup_logger

logger = setup_logger(__name__)

def search_cache2(query, config):
    logger.info("Started getting Real-Debrid link")
    
    headers = {
        "Authorization": f"Bearer {config['debridKey']}"
    }
    logger.info("RD: " + config['debridKey'])
    logger.info("Query: " + query)
    
    params = {
        'query': query,
        'limit': 10  # Limite de résultats, vous pouvez ajuster ce nombre
    }
    response = requests.get('https://api.real-debrid.com/rest/1.0/torrents/search', headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        logger.info(f"Erreur: {response.status_code} - {response.text}")
        return None


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

# Écrire les résultats dans un fichier .txt
#    try:
#        with open('cache_results.txt', 'w') as file:
#            file.write(json.dumps(cache_results, indent=4))
#        logger.info("Cache results successfully written to cache_results.txt")
#    except IOError as e:
#        logger.error(f"Failed to write cache results to file: {e}")


    # Extraire uniquement les titres
    #titles = [result.get('title', 'No Title') for result in cache_results]
    
    # Écrire les titres dans un fichier .txt
   # try:
   #     with open('cache_results.txt', 'w') as file:
   #         for title in titles:
   #             file.write(title + '\n')
   #     logger.info("Cache results successfully written to cache_results.txt")
   # except IOError as e:
   #     logger.error(f"Failed to write cache results to file: {e}") 

    return cache_results
