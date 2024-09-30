[![Static Badge](https://img.shields.io/badge/Telegram-Channel-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/+jJhUfsfFCn4zZDk0)      [![Static Badge](https://img.shields.io/badge/Telegram-Bot%20Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/dotcoin_bot?start=r_525256526)


![img1](.github/images/demo.png)

> README in Russian available [here](README-RU.md)

## Functionality
| Functional                                               | Supported |
|----------------------------------------------------------|:---------:|
| Multithreading                                           |     ✅     |
| Binding a proxy to a session                             |     ✅     |
| Auto-purchase of items if you have coins (tap, attempts) |     ✅     |
| Auto get all task if possible                            |     ✅     |
| Random sleep time between clicks                         |     ✅     |
| Random number of clicks per request                      |     ✅     |
| Support telethon .session                                |     ✅     |


## [Settings](https://github.com/SudoLite/DotCoinBot/blob/main/.env-example)
| Setup                          | Description                                                                                                                                                                                                                                   |
|--------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **API_ID / API_HASH**          | Platform data from which to launch a Telegram session (stock - Android)                                                                                                                                                                       |
| **GLOBAL_CONFIG_PATH**         | Specifies the global path for accounts_config, proxies, sessions. <br/>Specify an absolute path or use an environment variable (default environment variable: **TG_FARM**) <br/>If no environment variable exists, uses the script directory. |
| **REF_ID**                     | Your referral id after startapp=                                                                                                                                                                                                              |
| **AUTO_UPGRADE_TAP**           | Should I improve the tap _(True / False)_                                                                                                                                                                                                     |
| **MAX_TAP_LEVEL**              | Maximum level of tap pumping _(up to 15)_                                                                                                                                                                                                     |
| **AUTO_UPGRADE_ATTEMPTS**      | Should I improve the limit attempts _(True / False)_                                                                                                                                                                                          |
| **MAX_ATTEMPTS_LEVEL**         | Maximum level of limit attempts _(up to 15)_                                                                                                                                                                                                  |
| **RANDOM_TAPS_COUNT**          | Random number of taps _(eg [50,200])_                                                                                                                                                                                                         |
| **SLEEP_BETWEEN_TAP**          | Random delay between taps in seconds _(eg [10,25])_                                                                                                                                                                                           |
| **SESSIONS_PER_PROXY**         | Amount of sessions, that can share same proxy ( **1** )                                                                                                                                                                                       |
| **RANDOM_SESSION_START_DELAY** | Random delay at session start from 1 to set value (e.g. **30**)                                                                                                                                                                               |
| **USE_PROXY_FROM_FILE**        | Whether to use a proxy from the `bot/config/proxies.txt` file (**True** / False)                                                                                                                                                              |
| **DISABLE_PROXY_REPLACE**      | Disable automatic checking and replacement of non-working proxies before startup (True / **False**)                                                                                                                                           |
| **DEVICE_PARAMS**              | Enter device settings to make the telegram session look more realistic  (True / **False**)                                                                                                                                                    |
| **DEBUG_LOGGING**              | Whether to log error's tracebacks to /logs folder (True / **False**)                                                                                                                                                                          |

## Installation
You can download [**Repository**](https://github.com/SP-l33t/DotCoin-Telethon) by cloning it to your system and installing the necessary dependencies:
```shell
~ >>> git clone https://github.com/SP-l33t/DotCoin-Telethon.git
~ >>> cd DotCoinBot

#Linux
~/DotCoinBot >>> python3 -m venv venv
~/DotCoinBot >>> source venv/bin/activate
~/DotCoinBot >>> pip3 install -r requirements.txt
~/DotCoinBot >>> cp .env-example .env
~/DotCoinBot >>> nano .env # Here you must specify your API_ID and API_HASH , the rest is taken by default
~/DotCoinBot >>> python3 main.py

#Windows
~/DotCoinBot >>> python -m venv venv
~/DotCoinBot >>> venv\Scripts\activate
~/DotCoinBot >>> pip install -r requirements.txt
~/DotCoinBot >>> copy .env-example .env
~/DotCoinBot >>> # Specify your API_ID and API_HASH, the rest is taken by default
~/DotCoinBot >>> python main.py
```

Also for quick launch you can use arguments, for example:
```shell
~/DotCoinBot >>> python3 main.py --action (1/2)
# Or
~/DotCoinBot >>> python3 main.py -a (1/2)

#1 - Create session
#2 - Run clicker
```
