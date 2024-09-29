from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str
    GLOBAL_CONFIG_PATH: str = "TG_FARM"

    REF_ID: str = 'r_525256526'

    AUTO_UPGRADE_TAP: bool = True
    MAX_TAP_LEVEL: int = 11
    AUTO_UPGRADE_ATTEMPTS: bool = True
    MAX_ATTEMPTS_LEVEL: int = 11
    BET_AMOUNT: int = 150000
    RANDOM_TAPS_COUNT: list[int] = [10_000, 19_000]
    SLEEP_BETWEEN_TAP: list[int] = [10, 25]

    RANDOM_SESSION_START_DELAY: int = 30
    SESSIONS_PER_PROXY: int = 1
    USE_PROXY_FROM_FILE: bool = True
    USE_PROXY_CHAIN: bool = False

    DEVICE_PARAMS: bool = False

    DEBUG_LOGGING: bool = False


settings = Settings()
