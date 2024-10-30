import asyncio
import json
from aiohttp import request
from bot.config import settings

data_url = "https://github.com/SP-l33t/Auxiliary-Data/raw/refs/heads/main/cvd.json"


async def update_youtube_data():
    async with request(url=data_url, method="GET") as response:
        if response.status in range(200, 300):
            return (json.loads(await response.text())).get("youtube", {})
    return {}


async def update_youtube_routine(sleep_time: int = 43200):
    yt_data = await update_youtube_data()
    settings.YOUTUBE_DATA = yt_data if yt_data else settings.YOUTUBE_DATA
    await asyncio.sleep(sleep_time)
