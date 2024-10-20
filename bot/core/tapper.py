import aiohttp
import asyncio
import json
import re
import time
from urllib.parse import unquote, quote, parse_qs
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from datetime import datetime, timedelta, timezone
from random import randint, uniform
from time import time

from bot.utils.universal_telegram_client import UniversalTelegramClient

from bot.config import settings
from bot.utils import logger, log_error, config_utils, CONFIG_PATH, first_run
from bot.exceptions import InvalidSession
from .headers import headers, get_sec_ch_ua

CATS_API_URL = "https://api.catsdogs.live"


class Tapper:
    def __init__(self, tg_client: UniversalTelegramClient):
        self.tg_client = tg_client
        self.session_name = tg_client.session_name

        session_config = config_utils.get_session_config(self.session_name, CONFIG_PATH)

        if not all(key in session_config for key in ('api', 'user_agent')):
            logger.critical(self.log_message('CHECK accounts_config.json as it might be corrupted'))
            exit(-1)

        self.headers = headers
        user_agent = session_config.get('user_agent')
        self.headers['user-agent'] = user_agent
        self.headers.update(**get_sec_ch_ua(user_agent))

        self.proxy = session_config.get('proxy')
        if self.proxy:
            proxy = Proxy.from_str(self.proxy)
            self.tg_client.set_proxy(proxy)

        self.start_param = None

        self.user_data = None
        self._webview_data = None

    def log_message(self, message) -> str:
        return f"<ly>{self.session_name}</ly> | {message}"

    async def get_tg_web_data(self) -> str:
        webview_url = await self.tg_client.get_app_webview_url('catsdogs_game_bot', "join", "525256526")

        tg_web_data = unquote(unquote(string=webview_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
        self.user_data = json.loads(parse_qs(tg_web_data).get('user', [''])[0])

        user_data = re.findall(r'user=([^&]+)', tg_web_data)[0]
        chat_instance = re.findall(r'chat_instance=([^&]+)', tg_web_data)[0]
        chat_type = re.findall(r'chat_type=([^&]+)', tg_web_data)[0]
        start_param = re.findall(r'start_param=([^&]+)', tg_web_data)
        self.start_param = int(start_param[0]) if start_param else None
        auth_date = re.findall(r'auth_date=([^&]+)', tg_web_data)[0]
        hash_value = re.findall(r'hash=([^&]+)', tg_web_data)[0]

        user_data_encoded = quote(user_data)
        start_param = f"start_param={self.start_param}" if self.start_param else ""
        init_data = (f"user={user_data_encoded}&chat_instance={chat_instance}&chat_type={chat_type}&"
                     f"{start_param}&auth_date={auth_date}&hash={hash_value}")

        return init_data

    async def login(self, http_client: aiohttp.ClientSession):
        try:

            response = await http_client.get(f"{CATS_API_URL}/user/info")

            if response.status == 404 or response.status == 400:
                inviter = {"inviter_id": self.start_param} if self.start_param else {}
                response = await http_client.post(f"{CATS_API_URL}/auth/register",
                                                  json={**inviter, "race": 1})
                response.raise_for_status()
                logger.success(self.log_message(f"User successfully registered!"))
                await asyncio.sleep(delay=2)
                return await self.login(http_client)

            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except Exception as error:
            log_error(self.log_message(f"Unknown error when logging: {error}"))
            await asyncio.sleep(delay=randint(3, 7))

    async def check_proxy(self, http_client: aiohttp.ClientSession) -> bool:
        proxy_conn = http_client.connector
        if proxy_conn and not hasattr(proxy_conn, '_proxy_host'):
            logger.info(self.log_message(f"Running Proxy-less"))
            return True
        try:
            response = await http_client.get(url='https://ifconfig.me/ip', timeout=aiohttp.ClientTimeout(15))
            logger.info(self.log_message(f"Proxy IP: {await response.text()}"))
            return True
        except Exception as error:
            proxy_url = f"{proxy_conn._proxy_type}://{proxy_conn._proxy_host}:{proxy_conn._proxy_port}"
            log_error(self.log_message(f"Proxy: {proxy_url} | Error: {type(error).__name__}"))
            return False

    async def processing_tasks(self, http_client: aiohttp.ClientSession):
        try:
            tasks_req = await http_client.get(f"{CATS_API_URL}/tasks/list")
            tasks_req.raise_for_status()
            tasks_json = await tasks_req.json()

            for task in tasks_json:
                await asyncio.sleep(uniform(1, 3))
                if task.get('hidden'):
                    continue
                skip_task_ids = [44]
                if not task['transaction_id'] and task['id'] not in skip_task_ids:
                    if task.get('channel_id') and task.get('type') != 'invite':
                        if not settings.CHANNEL_SUBSCRIBE_TASKS:
                            continue
                        url = task['link']
                        logger.info(self.log_message(f"Performing TG subscription to <lc>{url}</lc>"))
                        await self.tg_client.join_and_mute_tg_channel(url)
                        result = await self.verify_task(http_client, task['id'])
                    elif task.get('type') != 'invite':
                        logger.info(self.log_message(f"Performing <lc>{task['title']}</lc> task"))
                        result = await self.verify_task(http_client, task['id'])
                    else:
                        continue

                    if result:
                        logger.success(self.log_message(f"Task <lc>{task['title']}</lc> completed! |"
                                       f" Reward: <e>+{task['amount']}</e> FOOD"))
                    else:
                        logger.info(self.log_message(f"Task <lc>{task['title']}</lc> not completed"))

                    await asyncio.sleep(delay=randint(5, 10))

        except Exception as error:
            log_error(self.log_message(f"Unknown error when processing tasks: {error}"))
            await asyncio.sleep(delay=3)

    async def get_balance(self, http_client: aiohttp.ClientSession):
        try:
            balance_req = await http_client.get('https://api.catsdogs.live/user/balance')
            balance_req.raise_for_status()
            balance_json = await balance_req.json()
            balance = 0
            for value in balance_json.values():
                if isinstance(value, int):
                    balance += value
            return balance
        except Exception as error:
            log_error(self.log_message(f"Unknown error when processing tasks: {error}"))
            await asyncio.sleep(delay=3)

    async def verify_task(self, http_client: aiohttp.ClientSession, task_id: int):
        try:
            response = await http_client.post(f'https://api.catsdogs.live/tasks/claim', json={'task_id': task_id})
            response.raise_for_status()
            response_json = await response.json()
            for value in response_json.values():
                if value == 'success':
                    return True
            return False

        except Exception as e:
            log_error(self.log_message(f"Unknown error while verifying task {task_id} | Error: {e}"))
            await asyncio.sleep(delay=3)

    async def claim_reward(self, http_client: aiohttp.ClientSession):
        try:
            result = False
            last_claimed = await http_client.get('https://api.catsdogs.live/user/info')
            last_claimed.raise_for_status()
            last_claimed_json = await last_claimed.json()
            claimed_at = last_claimed_json['claimed_at']
            available_to_claim, current_time = None, datetime.now(timezone.utc)
            if claimed_at:
                claimed_at = claimed_at.replace("Z", "+00:00")
                date_part, rest = claimed_at.split('.')
                time_part, timez = rest.split('+')
                microseconds = time_part.ljust(6, '0')
                claimed_at = f"{date_part}.{microseconds}+{timez}"

                available_to_claim = datetime.fromisoformat(claimed_at) + timedelta(hours=8)
            if not claimed_at or current_time > available_to_claim:
                response = await http_client.post('https://api.catsdogs.live/game/claim')
                response.raise_for_status()
                response_json = await response.json()
                result = True

            return result

        except Exception as e:
            log_error(self.log_message(f"Unknown error while claming game reward | Error: {e}"))
            await asyncio.sleep(delay=3)

    async def run(self) -> None:
        random_delay = uniform(1, settings.SESSION_START_DELAY)
        logger.info(self.log_message(f"Bot will start in <ly>{int(random_delay)}s</ly>"))
        await asyncio.sleep(random_delay)

        access_token_created_time = 0
        tg_web_data = None

        proxy_conn = {'connector': ProxyConnector.from_url(self.proxy)} if self.proxy else {}
        async with CloudflareScraper(headers=self.headers, timeout=aiohttp.ClientTimeout(60), **proxy_conn) as http_client:
            while True:
                if not await self.check_proxy(http_client=http_client):
                    logger.warning(self.log_message('Failed to connect to proxy server. Sleep 5 minutes.'))
                    await asyncio.sleep(300)
                    continue

                token_live_time = randint(3500, 3600)
                try:
                    if time() - access_token_created_time >= token_live_time or not tg_web_data:
                        tg_web_data = await self.get_tg_web_data()

                        if not tg_web_data:
                            logger.warning(self.log_message('Failed to get webview URL'))
                            await asyncio.sleep(300)
                            continue

                        http_client.headers["X-Telegram-Web-App-Data"] = tg_web_data

                        user_info = await self.login(http_client=http_client)
                        if user_info:
                            if self.tg_client.is_fist_run:
                                await first_run.append_recurring_session(self.session_name)
                        access_token_created_time = time()
                        sleep_time = randint(settings.SLEEP_TIME[0], settings.SLEEP_TIME[1])

                        await asyncio.sleep(delay=uniform(1, 3))

                        balance = await self.get_balance(http_client)
                        logger.info(self.log_message(f"Balance: <e>{balance}</e> $FOOD"))

                        if settings.AUTO_TASK:
                            await asyncio.sleep(delay=uniform(5, 10))
                            await self.processing_tasks(http_client=http_client)

                        if settings.CLAIM_REWARD:
                            reward_status = await self.claim_reward(http_client=http_client)
                            logger.info(self.log_message(f"Claim reward: {reward_status}"))

                        logger.info(self.log_message(f"Sleep <y>{round(sleep_time / 60, 1)}</y> min"))
                        await asyncio.sleep(delay=sleep_time)

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    err_sleep = uniform(60, 120)
                    log_error(self.log_message(f"Unknown error: {error}. Sleeping {int(err_sleep)}"))
                    await asyncio.sleep(err_sleep)


async def run_tapper(tg_client: UniversalTelegramClient):
    runner = Tapper(tg_client=tg_client)
    try:
        await runner.run()
    except InvalidSession as e:
        logger.error(runner.log_message(f"Invalid Session: {e}"))
