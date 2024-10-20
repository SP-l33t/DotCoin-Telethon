[![Static Badge](https://img.shields.io/badge/Telegram-Channel-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/+jJhUfsfFCn4zZDk0)      [![Static Badge](https://img.shields.io/badge/Telegram-Bot%20Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/dotcoin_bot?start=r_525256526)

## Рекомендация перед использованием

# 🔥🔥 Используйте PYTHON версии 3.10 🔥🔥

> 🇪🇳 README in english available [here](README)

## Функционал  
|                            Функционал                             | Поддерживается |
|:-----------------------------------------------------------------:|:--------------:|
|                          Многопоточность                          |       ✅        |
|                     Привязка прокси к сессии                      |       ✅        |
| Автоматическая покупка предметов при наличии монет (тап, попытки) |       ✅        |
|     Автоматическое получение всех заданий, если это возможно      |       ✅        |
|                Случайное время сна между нажатиями                |       ✅        |
|            Случайное количество кликов на один запрос             |       ✅        |
|              Поддержка telethon И pyrogram .session               |       ✅        |

_Скрипт осуществляет поиск файлов сессий в следующих папках:_
* /sessions
* /sessions/pyrogram
* /session/telethon


## [Настройки](https://github.com/SP-l33t/DotCoin-Telethon/blob/main/.env-example/)
|           Настройка            |                                                                                                                              Описание                                                                                                                               |
|:------------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|           **API_ID**           |                                                                                                                  Ваш Telegram API ID (целое число)                                                                                                                  |
|          **API_HASH**          |                                                                                                                   Ваш Telegram API Hash (строка)                                                                                                                    |
|     **GLOBAL_CONFIG_PATH**     | Определяет глобальный путь для accounts_config, proxies, sessions. <br/>Укажите абсолютный путь или используйте переменную окружения (по умолчанию - переменная окружения: **TG_FARM**)<br/> Если переменной окружения не существует, использует директорию скрипта |
|          **FIX_CERT**          |                                                                                              Попытаться исправить ошибку SSLCertVerificationError ( True / **False** )                                                                                              |
|           **REF_ID**           |                                                                                                                 Ваш реферальный ID после startapp=                                                                                                                  |
|      **AUTO_UPGRADE_TAP**      |                                                                                                  Включить автоматиеское улучшение уровня тапов ( **True** / False)                                                                                                  |         
|       **MAX_TAP_LEVEL**        |                                                                                                      Максимальный уровень прокачки тапа ( от 1 до 15, **5** )                                                                                                       |
|   **AUTO_UPGRADE_ATTEMPTS**    |                                                                                                Включить автоматическое улучшения количество игр ( **True** / False )                                                                                                |
|     **MAX_ATTEMPTS_LEVEL**     |                                                                                                  Максимальный уровень прокачки количества игр ( от 1 до 15, **5**)                                                                                                  |
|     **RANDOM_TAPS_COUNT**      |                                                                                                          Случайное количество нажатий (например [50, 200])                                                                                                          |
|     **SLEEP_BETWEEN_TAP**      |                                                                                                Случайная задержка между нажатиями (интервал, в секундах) ([10, 25])                                                                                                 |
| **RANDOM_SESSION_START_DELAY** |                                                                                           Случайная задержка при запуске. От 1 до указанного значения (например, **30**)                                                                                            |
|     **SESSIONS_PER_PROXY**     |                                                                                           Количество сессий, которые могут использовать один прокси (По умолчанию **1** )                                                                                           |
|    **USE_PROXY_FROM_FILE**     |                                                                                              Использовать прокси из файла `bot/config/proxies.txt` (**True** / False)                                                                                               |
|   **DISABLE_PROXY_REPLACE**    |                                                                                   Отключить автоматическую проверку и замену нерабочих прокси перед стартом ( True / **False** )                                                                                    |
|       **DEVICE_PARAMS**        |                                                                                  Вводить параметры устройства, чтобы сделать сессию более похожую, на реальную  (True / **False**)                                                                                  |
|       **DEBUG_LOGGING**        |                                                                                               Включить логирование трейсбэков ошибок в папку /logs (True / **False**)                                                                                               |

## Быстрый старт 📚

Для быстрой установки и последующего запуска - запустите файл run.bat на Windows или run.sh на Линукс

## Предварительные условия
Прежде чем начать, убедитесь, что у вас установлено следующее:
- [Python](https://www.python.org/downloads/) **версии 3.10**

## Получение API ключей
1. Перейдите на сайт [my.telegram.org](https://my.telegram.org) и войдите в систему, используя свой номер телефона.
2. Выберите **"API development tools"** и заполните форму для регистрации нового приложения.
3. Запишите `API_ID` и `API_HASH` в файле `.env`, предоставленные после регистрации вашего приложения.

## Установка
Вы можете скачать [**Репозиторий**](https://github.com/SP-l33t/DotCoin-Telethon) клонированием на вашу систему и установкой необходимых зависимостей:
```shell
git clone https://github.com/SP-l33t/DotCoin-Telethon.git
cd Tomarket
```

Затем для автоматической установки введите:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux ручная установка
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Здесь вы обязательно должны указать ваши API_ID и API_HASH , остальное берется по умолчанию
python3 main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/Tomarket >>> python3 main.py --action (1/2)
# Или
~/Tomarket >>> python3 main.py -a (1/2)

# 1 - Запускает кликер
# 2 - Создает сессию
```


# Windows ручная установка
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Указываете ваши API_ID и API_HASH, остальное берется по умолчанию
python main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/Tomarket >>> python main.py --action (1/2)
# Или
~/Tomarket >>> python main.py -a (1/2)

# 1 - Запускает кликер
# 2 - Создает сессию
```
