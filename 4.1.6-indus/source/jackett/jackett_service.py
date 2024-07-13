import os
import queue
import threading
import time
import xml.etree.ElementTree as ET

import requests

from concurrent.futures import ThreadPoolExecutor, as_completed

from jackett.jackett_indexer import JackettIndexer
from jackett.jackett_result import JackettResult
from models.movie import Movie
from models.series import Series
from utils import detection
from utils.logger import setup_logger


class JackettService:
    def __init__(self, config):
        self.logger = setup_logger(__name__)
        required_keys = ['jackettApiKey', 'jackettHost']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")
        self.__api_key = config['jackettApiKey']
        self.__base_url = f"{config['jackettHost']}/api/v2.0"
        self.__session = requests.Session()

    def search(self, media: Union[Movie, Series]) -> List[JackettResult]:
        self.logger.info(f"Started Jackett search for a {media.type} with title {media.titles[0]}")

        indexers = self.__get_indexers()
        results_queue = queue.Queue()

        def thread_target(media, indexer):
            self.logger.info(f"Searching on {indexer.title}")
            start_time = time.time()

            if isinstance(media, Movie):
                result = self.__search_movie_indexer(media, indexer)
            elif isinstance(media, Series):
                result = self.__search_series_indexer(media, indexer)
            else:
                raise TypeError("Only Movie and Series are allowed as media!")

            self.logger.info(
                f"Search on {indexer.title} took {time.time() - start_time} seconds and found {len(result)} results")

            results_queue.put(result)

        with ThreadPoolExecutor(max_workers=len(indexers)) as executor:
            futures = [executor.submit(thread_target, media, indexer) for indexer in indexers]

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.logger.exception("An exception occurred during threaded search execution.")
        
        results = []
        while not results_queue.empty():
            results.extend(results_queue.get())

        flatten_results = [result for sublist in results for result in sublist]
        return self.__post_process_results(flatten_results, media)

    def __search_indexer(self, media: Union[Movie, Series], indexer: JackettIndexer, media_type: str) -> List[JackettResult]:
        has_imdb_search_capability = (
            os.getenv("DISABLE_JACKETT_IMDB_SEARCH") != "true" 
            and ((indexer.movie_search_capatabilities if media_type == 'movie' else indexer.tv_search_capatabilities) is not None) 
            and 'imdbid' in (indexer.movie_search_capatabilities if media_type == 'movie' else indexer.tv_search_capatabilities)
        )

        if has_imdb_search_capability:
            languages = ['en']
            index_of_language = [index for index, lang in enumerate(media.languages) if lang == 'en'][0]
            titles = [media.titles[index_of_language]]
        elif indexer.language == "en":
            languages = media.languages
            titles = media.titles
        else:
            index_of_language = [index for index, lang in enumerate(media.languages) if lang == indexer.language or lang == 'en']
            languages = [media.languages[index] for index in index_of_language]
            titles = [media.titles[index] for index in index_of_language]

        results = []

        for index, lang in enumerate(languages):
            params = {
                'apikey': self.__api_key,
                't': media_type,
                'cat': '2000' if media_type == 'movie' else '5000',
                'q': titles[index],
                'year': getattr(media, 'year', None),
            }

            if has_imdb_search_capability:
                params['imdbid'] = media.id

            if media_type == 'series':
                params['season'] = str(int(media.season.replace('S', '')))
                params['ep'] = str(int(media.episode.replace('E', '')))

            url = f"{self.__base_url}/indexers/{indexer.id}/results/torznab/api"
            url += '?' + '&'.join([f'{k}={v}' for k, v in params.items()])

            try:
                response = self.__session.get(url)
                response.raise_for_status()
                results.append(self.__get_torrent_links_from_xml(response.text))
            except Exception:
                self.logger.exception(
                    f"An exception occurred while searching for a {media_type} on Jackett with indexer {indexer.title} and language {lang}.")

        return results

    def __search_movie_indexer(self, movie: Movie, indexer: JackettIndexer) -> List[JackettResult]:
        return self.__search_indexer(movie, indexer, 'movie')

    def __search_series_indexer(self, series: Series, indexer: JackettIndexer) -> List[JackettResult]:
        return self.__search_indexer(series, indexer, 'series')

    def __get_indexers(self) -> List[JackettIndexer]:
        url = f"{self.__base_url}/indexers/all/results/torznab/api?apikey={self.__api_key}&t=indexers&configured=true"

        try:
            response = self.__session.get(url)
            response.raise_for_status()
            return self.__get_indexer_from_xml(response.text)
        except Exception:
            self.logger.exception("An exception occurred while getting indexers from Jackett.")
            return []

    def __get_indexer_from_xml(self, xml_content: str) -> List[JackettIndexer]:
        xml_root = ET.fromstring(xml_content)

        indexer_list = []
        for item in xml_root.findall('.//indexer'):
            indexer = JackettIndexer()

            indexer.title = item.find('title').text
            indexer.id = item.attrib['id']
            indexer.link = item.find('link').text
            indexer.type = item.find('type').text
            indexer.language = item.find('language').text.split('-')[0]

            self.logger.info(f"Indexer: {indexer.title} - {indexer.link} - {indexer.type}")

            movie_search = item.find('.//searching/movie-search[@available="yes"]')
            tv_search = item.find('.//searching/tv-search[@available="yes"]')

            if movie_search is not None:
                indexer.movie_search_capatabilities = movie_search.attrib['supportedParams'].split(',')
            else:
                self.logger.info(f"Movie search not available for {indexer.title}")

            if tv_search is not None:
                indexer.tv_search_capatabilities = tv_search.attrib['supportedParams'].split(',')
            else:
                self.logger.info(f"TV search not available for {indexer.title}")

            indexer_list.append(indexer)

        return indexer_list

    def __get_torrent_links_from_xml(self, xml_content: str) -> List[JackettResult]:
        xml_root = ET.fromstring(xml_content)

        result_list = []
        for item in xml_root.findall('.//item'):
            result = JackettResult()

            result.seeders = item.find('.//torznab:attr[@name="seeders"]', namespaces={'torznab': 'http://torznab.com/schemas/2015/feed'}).attrib['value']
            if int(result.seeders) <= 0:
                continue

            result.title = item.find('title').text
            result.size = item.find('size').text
            result.link = item.find('link').text
            result.indexer = item.find('jackettindexer').text
            result.privacy = item.find('type').text

            magnet = item.find('.//torznab:attr[@name="magneturl"]', namespaces={'torznab': 'http://torznab.com/schemas/2015/feed'})
            result.magnet = magnet.attrib['value'] if magnet is not None else None

            infoHash = item.find('.//torznab:attr[@name="infohash"]', namespaces={'torznab': 'http://torznab.com/schemas/2015/feed'})
            result.info_hash = infoHash.attrib['value'] if infoHash is not None else None

            result_list.append(result)

        return result_list

    def __post_process_results(self, results: List[JackettResult], media: Union[Movie, Series]) -> List[JackettResult]:
        for result in results:
            result.languages = detection.detect_languages(result.title)
            result.quality = detection.detect_quality(result.title)
            result.quality_spec = detection.detect_quality_spec(result.title)
            result.type = media.type

            if isinstance(media, Series):
                result.season = media.season
                result.episode = media.episode

        return results
