#008
#

import asyncio
import base64
import json
import logging
import os
import re

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from dotenv import load_dotenv
from constants import NO_RESULTS
from utils.get_content import get_name
from utils.get_cached import search_cache
from utils.filter_results import filter_items
from utils.process_results import process_results
from utils.logger import setup_logger

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
        logger.info(f"{request.method} - {sensible_path}")
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

@app.get("/{config}/stream/{stream_type}/{stream_id}")
async def get_results(config: str, stream_type: str, stream_id: str):
    logger.info(f"Received config: {config}")
    logger.info(f"Received stream_type: {stream_type}")
    logger.info(f"Received stream_id: {stream_id}")
    
    stream_id = stream_id.replace(".json", "")
    logger.info(f"Processed stream_id: {stream_id}")

    config = json.loads(base64.b64decode(config).decode('utf-8'))
    logger.info(f"Decoded config: {config}")
    
    
    logger.info(f"{stream_type} request")
    logger.info("Getting name and properties")
    name = get_name(stream_id, stream_type, config=config)
    logger.info(f"Got name and properties: {name}")
    
    logger.info("Getting cached results")
    cached_results = search_cache(name)
    logger.info(f"Got {len(cached_results)} cached results: {cached_results}")
    
    logger.info("Filtering cached results")
    filtered_cached_results = filter_items(cached_results, stream_type, config=config, cached=True,
                                           season=name['season'] if stream_type == "series" else None,
                                           episode=name['episode'] if stream_type == "series" else None)
    logger.info(f"Filtered cached results: {len(filtered_cached_results)}")
    
    logger.info("Cached results found")
    logger.info("Processing cached results")
    stream_list = process_results(filtered_cached_results, True, stream_type,
                                  name['season'] if stream_type == "series" else None,
                                  name['episode'] if stream_type == "series" else None, config=config)
    logger.info(f"Processed cached results (total results: {len(stream_list)})")

    if len(stream_list) == 0:
        logger.info("No results found")
        return NO_RESULTS

    return {"streams": stream_list}

async def main():
    await asyncio.gather()

if __name__ == "__main__":
    asyncio.run(main())
