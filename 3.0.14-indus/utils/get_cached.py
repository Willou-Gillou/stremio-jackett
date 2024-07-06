import requests

from constants import CACHER_URL
from utils.logger import setup_logger

logger = setup_logger(__name__)


def search_cache(query):
    logger.info(query)
    url = CACHER_URL + "getResult/" + query['type'] + "/"
    response = requests.get(url, json=query)
    logger.info("\n" + 
    "---------------------------------------------------------------------------------------------------------------" + "\n" +
    "08 - SEARCH_CACHE function launched, sending request to https://stremio-jackett-cacher.elfhosted.com/ " + "\n" +
    "---------------------------------------------------------------------------------------------------------------" + "\n" +
    "******* formated URL for request : "+ str(url)+ "\n" +
    "******* number results : "+ query['type'] + "\n" +
    "******* full response : "+ str(response)+ "\n" +
    "******* returning result to main.py : ")

    return response.json()
