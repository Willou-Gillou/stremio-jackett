#17
import asyncio
import base64
import json
import logging
import os
import re
import shutil
import zipfile

import requests
import starlette.status as status
from aiocron import crontab
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from constants import NO_RESULTS
from debrid.alldebrid import get_stream_link_ad
from debrid.premiumize import get_stream_link_pm
from debrid.realdebrid import get_stream_link_rd
from utils.filter_results import filter_items
from utils.get_availability import availability
from utils.get_cached import search_cache
from utils.get_content import get_name
from utils.jackett import search
from utils.logger import setup_logger
from utils.process_results import process_results

load_dotenv()

root_path = os.environ.get("ROOT_PATH", None)
if root_path and not root_path.startswith("/"):
    root_path = "/" + root_path
app = FastAPI(root_path=root_path)

VERSION = "3.0.14"
isDev = os.getenv("NODE_ENV") == "development"


class LogFilterMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        request = Request(scope, receive)
        path = request.url.path
        sensible_path = re.sub(r'/ey.*?/', '/<SENSITIVE_DATA>/', path)
        logger.info(f"\n---------------------------------------------------\n01 - Info recieved from Addon, middleware initiated : \n---------------------------------------------------\n******* Data received : {request.method} - " + str(path) + "\n")
        return await self.app(scope, receive, send)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not isDev:
    app.add_middleware(LogFilterMiddleware)

templates = Jinja2Templates(directory=".")

logger = setup_logger(__name__)


@app.get("/")
async def root():
    return RedirectResponse(url="/configure")


@app.get("/configure")
async def configure(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/{config}/configure")
async def configure(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/{params}/manifest.json")
async def get_manifest():
    return {
        "id": "community.aymene69.jackett",
        "icon": "https://i.imgur.com/tVjqEJP.png",
        "version": VERSION,
        "catalogs": [],
        "resources": ["stream"],
        "types": ["movie", "series"],
        "name": "Jackett" + (" (Dev)" if isDev else ""),
        "description": "Elevate your Stremio experience with seamless access to Jackett torrent links, effortlessly "
                       "fetching torrents for your selected movies within the Stremio interface.",
        "behaviorHints": {
            "configurable": True,
        }
    }

formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                              '%m-%d %H:%M:%S')

logger.info("\n" + 
"-------------------------------"+ "\n" +
"->   Jackett Addon started   <-"+ "\n" +
"-------------------------------"+ "\n")

@app.get("/{config}/stream/{stream_type}/{stream_id}")
async def get_results(config: str, stream_type: str, stream_id: str):
    
    config1=config
    stream_id = stream_id.replace(".json", "")
    config = json.loads(base64.b64decode(config).decode('utf-8'))
    config['exclusion'].append('Unknown')
    config_en=config.copy()
    config_en['language'] = 'en'

    logger.info("\n" + 
    "---------------------------------------------------" + "\n" +
    "02 - GET_RESULT function launched, data collected :\n" +
    "---------------------------------------------------" + "\n" +
    "******* stream_id: "+ stream_id + "\n" +
    "******* stream_type: "+ stream_type + "\n" +
    "******* config: "+ config1[:20] + "...\n\n" +
    
    "------------------------" + "\n" +
    "03 - Decrypting $config :" + "\n" +
    "------------------------" + "\n" +
    "******* decrypted Config: "+ str(config)+ "\n\n" +
    
    "-----------------------------------------------------------------------------------------------------------------------" + "\n" +
    "04 - Calling GET_NAME function located in ./utils/get_content.py with $stream_id,$stream_type and decrypted $config info \n" +
    "-----------------------------------------------------------------------------------------------------------------------" + "\n\n")
    
    name = get_name(stream_id, stream_type, config=config)
    name_en = get_name(stream_id, stream_type, config=config_en)

    if config['cache']:
        logger.info("\n" + 
        "---------------------------------------------------------------------------------------------------------------" + "\n" +
        "07 - Calling SEARCH_CACHE function located in ./utils/get_cached.py with $name (title, year, type and language) " + "\n" +
        "---------------------------------------------------------------------------------------------------------------" + "\n")
        cached_results = search_cache(name)
        cached_results_en = search_cache(name_en)
        cached_results_all= cached_results + cached_results_en
        
        if len(cached_results_all) == 0:
            logger.info("Processed cached results : 0")
            return NO_RESULT
    
    else:
        cached_results_all = []
    
    logger.info("\n" + 
    "------------------------------------------------------------------------------------------------------------------------------------------------------" + "\n" +
    "09 - Calling FILTER_ITEMS function located in ./utils/filter_results.py with $cache_results, $stream_type, $config +  $season & $episode only if serie" + "\n" +
    "------------------------------------------------------------------------------------------------------------------------------------------------------" + "\n")

    filtered_cached_results = filter_items(cached_results_all, stream_type, config=config, cached=True,
                                           season=name['season'] if stream_type == "series" else None,
                                           episode=name['episode'] if stream_type == "series" else None)


    if len(filtered_cached_results) > 0:
        logger.info("\n" + 
            "-----------------------------------------------------------------------------------------------------------------------------------------------------------" + "\n" +
            "12 - Calling PROCESS_RESULTS function located in ./utils/process_results.py with $filtered_cached_results, $stream_type +  $season & $episode only if serie" + "\n" +
            "-----------------------------------------------------------------------------------------------------------------------------------------------------------" + "\n")

        stream_list = process_results(filtered_cached_results, True, stream_type,
                                      name['season'] if stream_type == "series" else None,
                                      name['episode'] if stream_type == "series" else None, config=config)
        logger.info("Processed cached results : " + str(len(stream_list)) + ")")
        if len(stream_list) == 0:
            logger.info("No results found")
            return NO_RESULTS
        return {"streams": stream_list}
    else:
        logger.info("Processed cached results : 0 ")
        return NO_RESULTS


@app.get("/playback/{config}/{query}/{title}")
async def get_playback(config: str, query: str, title: str, request: Request):
    try:
        if not query or not title:
            raise HTTPException(status_code=400, detail="Query and title are required.")
        config = json.loads(base64.b64decode(config).decode('utf-8'))
        logger.info("Decoding query")
        query = base64.b64decode(query).decode('utf-8')
        logger.info(query)
        logger.info("Decoded query")

        service = config['service']
        if service == "realdebrid":
            logger.info("Getting Real-Debrid link")
            source_ip = request.client.host
            link = get_stream_link_rd(query, source_ip, config=config)
        elif service == "alldebrid":
            logger.info("Getting All-Debrid link")
            link = get_stream_link_ad(query, config=config)
        elif service == "premiumize":
            logger.info("Getting Premiumize link")
            link = get_stream_link_pm(query, config=config)
        else:
            raise HTTPException(status_code=500, detail="Invalid service configuration.")

        logger.info("Got link: " + link)
        return RedirectResponse(url=link, status_code=status.HTTP_301_MOVED_PERMANENTLY)

    except Exception as e:
        logger.error('An error occured %s', 'division', exc_info=e)
        raise HTTPException(status_code=500, detail="An error occurred while processing the request.")


async def main():
    await asyncio.gather(
        # schedule_task()
    )


if __name__ == "__main__":
    asyncio.run(main())
