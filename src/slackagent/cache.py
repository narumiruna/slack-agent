import os
from functools import cache
from typing import Final

from aiocache import BaseCache
from aiocache import Cache
from loguru import logger

DEFAULT_REDIS_URL: Final[str] = "memory://"


@cache
def get_cache_from_env() -> BaseCache:
    url = os.getenv("CACHE_URL")
    if not url:
        logger.warning("No cache url provided, using {url}", url=DEFAULT_REDIS_URL)
        url = DEFAULT_REDIS_URL

    return Cache.from_url(url)
