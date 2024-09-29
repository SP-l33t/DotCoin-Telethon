import aiohttp
import asyncio
import fasteners
import inspect
import os
import random
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from datetime import datetime, timezone
from time import time
from urllib.parse import unquote

from telethon import TelegramClient
from telethon.errors import *
from telethon.types import InputUser, InputPeerUser
from telethon.functions import messages, contacts

from .agents import generate_random_user_agent
from bot.config import settings
from bot.utils import logger, log_error, proxy_utils, config_utils, CONFIG_PATH
from bot.exceptions import InvalidSession
from .headers import headers, get_sec_ch_ua


DOTCOIN_API = "https://api.dotcoin.bot"


class Tapper:
    def __init__(self, tg_client: TelegramClient):
        self.tg_client = tg_client
        self.session_name, _ = os.path.splitext(os.path.basename(tg_client.session.filename))
        self.config = config_utils.get_session_config(self.session_name, CONFIG_PATH)
        self.proxy = self.config.get('proxy', None)
        self.lock = fasteners.InterProcessLock(
            os.path.join(os.path.dirname(CONFIG_PATH), 'lock_files', f"{self.session_name}.lock"))
        self.headers = headers
        self.headers['User-Agent'] = self.check_user_agent()
        self.headers.update(**get_sec_ch_ua(self.headers.get('User-Agent', '')))

        self._webview_data = None

        if self.proxy:
            proxy = Proxy.from_str(self.proxy)
            proxy_dict = proxy_utils.to_telethon_proxy(proxy)
            self.tg_client.set_proxy(proxy_dict)

    def log_message(self, message) -> str:
        return f"<light-yellow>{self.session_name}</light-yellow> | {message}"

    def check_user_agent(self):
        user_agent = self.config.get('user_agent')
        if not user_agent:
            user_agent = generate_random_user_agent()
            self.config['user_agent'] = user_agent
            config_utils.update_session_config_in_file(self.session_name, self.config, CONFIG_PATH)

        return user_agent

    async def initialize_webview_data(self):
        if not self._webview_data:
            while True:
                try:
                    resolve_result = await self.tg_client(contacts.ResolveUsernameRequest(username='dotcoin_bot'))
                    user = resolve_result.users[0]
                    peer = InputPeerUser(user_id=user.id, access_hash=user.access_hash)
                    self._webview_data = {'peer': peer, 'bot': user.username}
                    break
                except FloodWaitError as fl:
                    fls = fl.seconds

                    logger.warning(self.log_message(f"FloodWait {fl}. Waiting {fls}s"))
                    await asyncio.sleep(fls + 3)

                except (UnauthorizedError, AuthKeyUnregisteredError):
                    raise InvalidSession(f"{self.session_name}: User is unauthorized")
                except (UserDeactivatedError, UserDeactivatedBanError, PhoneNumberBannedError):
                    raise InvalidSession(f"{self.session_name}: User is banned")

    async def get_tg_web_data(self) -> str | None:
        tg_web_data = None
        with self.lock:
            try:
                if not self.tg_client.is_connected():
                    await self.tg_client.connect()
                await self.initialize_webview_data()

                ref_id = settings.REF_ID if random.randint(0, 100) <= 85 else "r_525256526"

                start_state = False
                async for message in self.tg_client.iter_messages('dotcoin_bot'):
                    if r'/start' in message.text:
                        start_state = True
                        break
                if not start_state:
                    await self.tg_client(messages.StartBotRequest(bot=self._webview_data.get('peer'),
                                                                  peer=self._webview_data.get('peer'),
                                                                  start_param=ref_id))

                web_view = await self.tg_client(messages.RequestWebViewRequest(
                    **self._webview_data,
                    platform='android',
                    from_bot_menu=False,
                    url='https://app.dotcoin.bot',
                    start_param=ref_id
                ))

                auth_url = web_view.url
                tg_web_data = unquote(
                    string=unquote(
                        string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0]))

                user_id = tg_web_data.split('"id":')[1].split(',"first_name"')[0]
                self.headers['X-Telegram-User-Id'] = user_id

            except InvalidSession:
                raise

            except Exception as error:
                log_error(self.log_message(f"Unknown error during Authorization: {type(error).__name__}"))
                await asyncio.sleep(delay=3)

            finally:
                if self.tg_client.is_connected():
                    await self.tg_client.disconnect()
                    await asyncio.sleep(1)

        return tg_web_data

    async def get_token(self, http_client: aiohttp.ClientSession, tg_web_data: str) -> dict[str] | None:
        try:
            http_client.headers["Authorization"] = f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impqdm5tb3luY21jZXdudXlreWlkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDg3MDE5ODIsImV4cCI6MjAyNDI3Nzk4Mn0.oZh_ECA6fA2NlwoUamf1TqF45lrMC0uIdJXvVitDbZ8"
            http_client.headers["Content-Type"] = "application/json"
            logger.info(self.log_message(f"bot action: [{inspect.currentframe().f_code.co_name}]"))
            await asyncio.sleep(random.uniform(1, 3))
            response = await http_client.post(f'{DOTCOIN_API}/functions/v1/getToken', json={"initData": tg_web_data})
            response.raise_for_status()

            if response.ok:
                response_json = await response.json()
                return response_json
            else:
                return None

        except Exception as error:
            log_error(self.log_message(f"Unknown error when getting access token: {error}"))
            await asyncio.sleep(delay=10)

    async def get_profile_data(self, http_client: aiohttp.ClientSession) -> dict[str]:
        try:
            logger.info(self.log_message(f"bot action: [{inspect.currentframe().f_code.co_name}]"))
            await asyncio.sleep(random.uniform(1, 3))
            response = await http_client.post(f'{DOTCOIN_API}/rest/v1/rpc/get_user_info', json={})
            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except Exception as error:
            log_error(self.log_message(f"Unknown error when getting Profile Data: {error}"))
            await asyncio.sleep(delay=10)

    async def get_tasks_data(self, http_client: aiohttp.ClientSession, is_premium: bool) -> dict:
        try:
            logger.info(self.log_message(f"bot action: [{inspect.currentframe().f_code.co_name}]"))
            await asyncio.sleep(random.uniform(1, 3))
            response = await http_client.get(
                f'{DOTCOIN_API}/rest/v1/rpc/get_filtered_tasks?platform=android&locale=en&is_premium={is_premium}')
            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except Exception as error:
            log_error(self.log_message(f"Unknown error when getting Tasks Data: {error}"))
            await asyncio.sleep(delay=10)

    async def complete_task(self, http_client: aiohttp.ClientSession, task_id: int) -> bool:
        try:
            logger.info(self.log_message(f"bot action: [{inspect.currentframe().f_code.co_name}]"))
            await asyncio.sleep(random.uniform(1, 3))
            response = await http_client.post(f'{DOTCOIN_API}/rest/v1/rpc/complete_task', json={"oid": task_id})
            response.raise_for_status()
            response_json = await response.json()
            return response_json.get('success')

        except Exception as error:
            log_error(self.log_message(f"Unknown error when complate task: {error}"))
            await asyncio.sleep(delay=10)
            return False

    async def upgrade_boosts(self, http_client: aiohttp.ClientSession, boost_type: str, lvl: int) -> bool:
        try:
            logger.info(self.log_message(f"bot action: [{inspect.currentframe().f_code.co_name}]"))
            await asyncio.sleep(random.uniform(1, 3))
            response = await http_client.post(f'{DOTCOIN_API}/rest/v1/rpc/{boost_type}', json={"lvl": lvl})
            response.raise_for_status()

            if response.ok:
                response_json = await response.json()
                if response_json.get('success'):
                    return True
                else:
                    return False
            else:
                return False

        except Exception as error:
            log_error(self.log_message(f"Unknown error when upgrade_boosts: {error}"))
            await asyncio.sleep(delay=10)
            return False

    async def play_tap_game(self, http_client: aiohttp.ClientSession, taps: int):
        try:
            logger.info(self.log_message(f"bot action: [{inspect.currentframe().f_code.co_name}]"))
            await asyncio.sleep(random.uniform(1, 3))
            response = await http_client.post(f'{DOTCOIN_API}/rest/v1/rpc/save_coins', json={"coins": taps})
            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except Exception as error:
            log_error(self.log_message(f"Unknown error when saving coins: {error}"))
            await asyncio.sleep(delay=10)
            return False

    async def try_your_luck(self, http_client: aiohttp.ClientSession, luck_amount: int) -> bool:
        try:
            logger.info(self.log_message(f"bot action: [{inspect.currentframe().f_code.co_name}]"))
            await asyncio.sleep(random.uniform(1, 3))
            response = await http_client.post(f'{DOTCOIN_API}/rest/v1/rpc/try_your_luck', json={"coins": luck_amount})
            response.raise_for_status()
            response_json = await response.json()
            return response_json.get('success')

        except Exception as error:
            log_error(self.log_message(f"Unknown error when was treing to get luck: {error}"))
            await asyncio.sleep(delay=10)
            return False

    async def restore_attempt(self, http_client: aiohttp.ClientSession) -> bool:
        try:
            logger.info(self.log_message(f"bot action: [{inspect.currentframe().f_code.co_name}]"))
            await asyncio.sleep(random.uniform(1, 3))
            response = await http_client.post(f'{DOTCOIN_API}/rest/v1/rpc/restore_attempt', json={})
            response.raise_for_status()
            response_json = await response.json()
            return response_json.get('success')

        except Exception as error:
            log_error(self.log_message(f"Unknown error when was treing to restore attempt: {error}"))
            await asyncio.sleep(delay=10)
            return False

    async def get_assets(self, http_client: aiohttp.ClientSession) -> dict:
        try:
            logger.info(self.log_message(f"bot action: [{inspect.currentframe().f_code.co_name}]"))
            await asyncio.sleep(random.uniform(1, 3))
            response = await http_client.post(f'{DOTCOIN_API}/rest/v1/rpc/get_assets', json={})
            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except Exception as error:
            log_error(self.log_message(f"Unknown error when getting Assets Data: {error}"))
            await asyncio.sleep(delay=10)

    async def spin_to_earn(self, http_client: aiohttp.ClientSession) -> dict[str]:
        try:
            logger.info(self.log_message(f"bot action: [{inspect.currentframe().f_code.co_name}]"))
            await asyncio.sleep(random.uniform(1,3))
            response = await http_client.post(f'{DOTCOIN_API}/rest/v1/rpc/spin', json={})
            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except Exception as error:
            log_error(self.log_message(f"Unknown error when trying claim game 'Spin to Win': {error}"))
            await asyncio.sleep(delay=10)

    async def upgrade_dtc(self, http_client: aiohttp.ClientSession):
        try:
            logger.info(self.log_message(f"bot action: [{inspect.currentframe().f_code.co_name}]"))
            await asyncio.sleep(random.uniform(1,3))
            response = await http_client.post(f'{DOTCOIN_API}/functions/v1/upgradeDTCMiner')
            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except Exception as error:
            log_error(self.log_message(f"Unknown error when trying claim game 'Spin to Win': {error}"))
            await asyncio.sleep(delay=10)

    async def check_proxy(self, http_client: aiohttp.ClientSession) -> bool:
        proxy_conn = http_client._connector
        try:
            response = await http_client.get(url='https://ifconfig.me/ip', timeout=aiohttp.ClientTimeout(15))
            logger.info(self.log_message(f"Proxy IP: {await response.text()}"))
            return True
        except Exception as error:
            proxy_url = f"{proxy_conn._proxy_type}://{proxy_conn._proxy_host}:{proxy_conn._proxy_port}"
            log_error(self.log_message(f"Proxy: {proxy_url} | Error: {type(error).__name__}"))
            return False

    async def run(self) -> None:
        random_delay = random.randint(1, settings.RANDOM_SESSION_START_DELAY)
        logger.info(self.log_message(f"Bot will start in <light-red>{random_delay}s</light-red>"))
        await asyncio.sleep(delay=random_delay)

        access_token_created_time = 0
        tg_web_data = None

        proxy_conn = {'connector': ProxyConnector.from_url(self.proxy)} if self.proxy else {}
        async with CloudflareScraper(headers=self.headers, timeout=aiohttp.ClientTimeout(60), **proxy_conn) as http_client:
            while True:
                if not await self.check_proxy(http_client=http_client):
                    logger.warning(self.log_message('Failed to connect to proxy server. Sleep 5 minutes.'))
                    await asyncio.sleep(300)
                    continue

                token_live_time = random.randint(3500, 3600)

                try:
                    if time() - access_token_created_time >= token_live_time:
                        tg_web_data = await self.get_tg_web_data()

                        if not tg_web_data:
                            logger.warning(self.log_message('Failed to get webview URL'))
                            await asyncio.sleep(300)
                            continue

                    access_token_created_time = time()

                    get_token_data = await self.get_token(http_client=http_client, tg_web_data=tg_web_data)
                    access_token = get_token_data.get('token')
                    if not access_token:
                        logger.warning(self.log_message('Failed to log in. Retry in 5 minutes'))
                        await asyncio.sleep(300)
                        continue
                    logger.info(self.log_message(f"Successfully logged in"))

                    http_client.headers["Authorization"] = f"Bearer {access_token}"

                    profile_data = await self.get_profile_data(http_client=http_client)

                    if profile_data:
                        balance = profile_data.get('balance')
                        level = profile_data.get('level')
                        daily_attempts = profile_data.get('daily_attempts')
                        click_lvl = profile_data.get('multiple_clicks')  # Click power lvl
                        limit_attempts = profile_data.get('limit_attempts')  # Energy limit level
                        dtc_lvl = profile_data.get('dtc_level')  # DTC Farming level

                        logger.info(self.log_message(f"Level: <c>{level}</c>, Balance: <c>{balance}</c>, | "
                                                     f"Daily_Attempts: <c>{daily_attempts}</c>, Click_Level: <c>{click_lvl}</c>,"
                                                     f"Energy_Level: <c>{limit_attempts}</c> , DTC_LVL: <c>{dtc_lvl}</c>"))
                    else:
                        logger.warning(self.log_message("Failed to get profile data"))

                    if profile_data.get('gamex2_times', 0) > 0:
                        get_lucky = await self.try_your_luck(http_client=http_client, luck_amount=settings.BET_AMOUNT)

                        if get_lucky:
                            logger.success(self.log_message(f"Won the gamble and received {settings.BET_AMOUNT} coints"))
                        else:
                            logger.info(self.log_message(f"Gamble failed. Lost {settings.BET_AMOUNT} coints"))

                    spin_updated_at = profile_data.get('spin_updated_at')

                    if not spin_updated_at:
                        spin_updated_atx = 0
                    else:
                        spin_updated_atx = int(datetime.fromisoformat(spin_updated_at).timestamp())

                    current_date_utc = int(datetime.now().astimezone(timezone.utc).timestamp())

                    if (spin_updated_atx + 28800) < current_date_utc:
                        asset_data = await self.get_assets(http_client=http_client)

                        dtc_asset = None
                        dtc_amount = 0

                        for index, value in enumerate(asset_data):
                            if value.get('name', "").lower() == 'dotcoin':
                                dtc_asset = value
                                dtc_amount = value.get('amount')

                        if dtc_asset and dtc_amount > 0:
                            spin_to_earn_response = await self.spin_to_earn(http_client=http_client)
                            logger.info(self.log_message(f"spin_to_earn_response: {spin_to_earn_response}"))

                            if spin_to_earn_response.get('success'):
                                logger.info(self.log_message(f"You won: {spin_to_earn_response.get('amount')} "
                                                             f"{spin_to_earn_response.get('symbol')}"))

                    restored_attempt = await self.restore_attempt(http_client=http_client)

                    while restored_attempt and daily_attempts < 10:
                        action = 'daily_attempts'
                        daily_attempts += 1
                        logger.info(self.log_message(f"Restore attempt: {restored_attempt}"))
                        logger.success(self.log_message(f"action: <red>[{action}]</red> - <c>{daily_attempts}</c>"))
                        restored_attempt = await self.restore_attempt(http_client=http_client)
                    else:
                        logger.info(self.log_message(f"Restore attempt: {restored_attempt}"))

                    tasks_data = await self.get_tasks_data(http_client=http_client,
                                                           is_premium=profile_data.get('is_premium', False))

                    for task in tasks_data:
                        task_id = task.get("id")
                        task_title = task.get("title")
                        task_reward = task.get("reward")
                        task_status = task.get("is_completed")

                        if task_status is True:
                            continue

                        if not task.get("url") and not task.get("image"):
                            continue

                        task_data_claim = await self.complete_task(http_client=http_client, task_id=task_id)
                        if task_data_claim:
                            logger.success(self.log_message(f"Successful claim task | Task Title: <c>{task_title}</c> "
                                                            f"| Task Reward: <g>+{task_reward}</g>"))
                            continue

                    while daily_attempts > 0:
                        taps = random.randint(*settings.RANDOM_TAPS_COUNT)
                        save_coins_data = await self.play_tap_game(http_client=http_client, taps=taps)
                        if save_coins_data.get('success'):
                            daily_attempts -= 1
                            logger.success(self.log_message(
                                f"action: <red>[save_coins/{taps}/{daily_attempts}]</red> - <c>{save_coins_data}</c>"))
                        else:
                            logger.warning(self.log_message(
                                f"action: <red>[save_coins/{taps}/{daily_attempts}]</red> - <c>{save_coins_data}</c>"))
                            break

                    profile_data = await self.get_profile_data(http_client=http_client)

                    balance = int(profile_data.get('balance'))
                    daily_attempts = int(profile_data.get('daily_attempts'))
                    multiple_lvl = profile_data.get('multiple_clicks')
                    attempts_lvl = profile_data.get('limit_attempts') - 9

                    next_multiple_lvl = multiple_lvl + 1
                    next_multiple_price = (2 ** multiple_lvl) * 1000
                    next_attempts_lvl = attempts_lvl + 1
                    next_attempts_price = (2 ** attempts_lvl) * 1000

                    dtc_upgrade = await self.upgrade_dtc(http_client)
                    if dtc_upgrade:
                        logger.success(self.log_message('Successfully upgraded DTC mining level'))

                    if settings.AUTO_UPGRADE_TAP and balance > next_multiple_price and next_multiple_lvl <= settings.MAX_TAP_LEVEL:
                        action = 'add_multitap'
                        logger.info(self.log_message(f"action: <red>[upgrade/{action}]</red> "))
                        status = await self.upgrade_boosts(http_client=http_client, boost_type=action, lvl=multiple_lvl)
                        if status:
                            logger.success(self.log_message(f"action: <red>[upgrade/{action}]</red> - <c>{status}</c>"))
                        else:
                            log_error(self.log_message(f"action: <red>[upgrade/{action}]</red> - <c>{status}</c>"))

                    if settings.AUTO_UPGRADE_ATTEMPTS and balance > next_attempts_price and next_attempts_lvl <= settings.MAX_ATTEMPTS_LEVEL:
                        action = 'add_attempts'
                        logger.info(self.log_message(f"action: <red>[upgrade/{action}]</red> "))
                        status = await self.upgrade_boosts(http_client=http_client, boost_type=action, lvl=multiple_lvl)
                        if status:
                            logger.success(self.log_message(f"action: <red>[upgrade/{action}]</red> - <c>{status}</c>"))
                        else:
                            log_error(self.log_message(f"action: <red>[upgrade/{action}]</red> - <c>{status}</c>"))

                    logger.info(self.log_message(f"Minimum attempts reached: {daily_attempts}"))
                    sleep_time = random.uniform(3600, 7200)
                    logger.info(self.log_message(f"Goint to Sleep. Next try to tap coins in {int(sleep_time)}s"))

                    await asyncio.sleep(sleep_time)

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    log_error(self.log_message(f"Unknown error: {error}"))
                    await asyncio.sleep(delay=300)


async def run_tapper(tg_client: TelegramClient):
    runner = Tapper(tg_client=tg_client)
    try:
        await runner.run()
    except InvalidSession as e:
        logger.error(runner.log_message(f"Invalid Session: {e}"))
