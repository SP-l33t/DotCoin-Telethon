import glob
import asyncio
import argparse
import os

from telethon import TelegramClient

from bot.config import settings
from bot.utils import logger, config_utils, proxy_utils, CONFIG_PATH, SESSIONS_PATH, PROXIES_PATH
from bot.core.tapper import run_tapper
from bot.core.registrator import register_sessions


start_text = """
<lc>
██████╗░░█████╗░████████╗░█████╗░░█████╗░██╗███╗░░██╗
██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗██║████╗░██║
██║░░██║██║░░██║░░░██║░░░██║░░╚═╝██║░░██║██║██╔██╗██║
██║░░██║██║░░██║░░░██║░░░██║░░██╗██║░░██║██║██║╚████║
██████╔╝╚█████╔╝░░░██║░░░╚█████╔╝╚█████╔╝██║██║░╚███║
╚═════╝░░╚════╝░░░░╚═╝░░░░╚════╝░░╚════╝░╚═╝╚═╝░░╚══╝</lc>

Select an action:

    1. Run clicker
    2. Create session
"""

API_ID = settings.API_ID
API_HASH = settings.API_HASH


def get_session_names(sessions_folder: str) -> list[str]:
    session_names = sorted(glob.glob(f"{sessions_folder}/*.session"))
    return [os.path.splitext(os.path.basename(file))[0] for file in session_names]


async def get_tg_clients() -> list[TelegramClient]:
    accounts_config = config_utils.read_config_file(CONFIG_PATH)
    session_names = get_session_names(SESSIONS_PATH)

    if not session_names:
        raise FileNotFoundError("Session files not found")

    tg_clients = []
    for session_name in session_names:
        session_config: dict = accounts_config.get(session_name, {})

        client_params = {
            "session": os.path.join(SESSIONS_PATH, session_name),
            "lang_code": "en",
            "system_lang_code": "en-US"
        }
        for key in ("api_id", "api_hash", "device_model", "system_version", "app_version"):
            if key in session_config and session_config[key]:
                client_params[key] = session_config[key]

        session_proxy = session_config.get('proxy')
        if not session_proxy and 'proxy' in session_config.keys():
            tg_clients.append(TelegramClient(**client_params))
            continue

        else:
            working_proxy = await proxy_utils.get_working_proxy(accounts_config, session_proxy)
            if not working_proxy:
                logger.warning(f"{session_name} | Didn't find a working unused proxy for session | Skipping")
                continue
            else:
                if 'api_id' in client_params and 'api_hash' in client_params:
                    tg_clients.append(TelegramClient(**client_params))
                    session_config['proxy'] = working_proxy
                    accounts_config[session_name] = session_config
                    config_utils.update_session_config_in_file(session_name, session_config, CONFIG_PATH)
                    continue
                else:
                    client_params['api_id'] = API_ID
                    client_params['api_hash'] = API_HASH
                    tg_clients.append(TelegramClient(**client_params))
                    session_config.update(
                        {
                            'proxy': working_proxy if settings.USE_PROXY_FROM_FILE else None,
                            'api_id': API_ID,
                            'api_hash': API_HASH
                        })
                    accounts_config[session_name] = session_config
                    config_utils.update_session_config_in_file(session_name, session_config, CONFIG_PATH)
                    continue

    return tg_clients


async def process() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=int, help="Action to perform")

    if not settings.USE_PROXY_FROM_FILE:
        logger.info(f"Detected {len(get_session_names(SESSIONS_PATH))} sessions | USE_PROXY_FROM_FILE=False")
    else:
        logger.info(f"Detected {len(get_session_names(SESSIONS_PATH))} sessions | "
                    f"{len(proxy_utils.get_proxies(PROXIES_PATH))} proxies")

    action = parser.parse_args().action

    if not action:
        logger.info(start_text)

        while True:
            action = input("> ").strip()

            if not action.isdigit():
                logger.warning("Action must be number")
            elif action not in ["1", "2"]:
                logger.warning("Action must be 1 or 2")
            else:
                action = int(action)
                break

    if action == 1:
        if not API_ID or not API_HASH:
            raise ValueError("API_ID and API_HASH not found in the .env file.")
        await run_tasks()
    elif action == 2:
        await register_sessions()


async def run_tasks():
    tg_clients = await get_tg_clients()

    tasks = [
        asyncio.create_task(
            run_tapper(
                tg_client=tg_client
            )
        )
        for tg_client in tg_clients
    ]

    await asyncio.gather(*tasks)
