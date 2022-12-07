import os
import pathlib

from pydantic.env_settings import BaseSettings
import environ

env = environ.Env()


class Settings(BaseSettings):
    sbercat_app_endpoint: str = env.str(
        "SBERCAT_APP_ENDPOINT", default="https://sbercat-shelter.ru-prod2.kts.studio/api/{action}"
    )
    sbercat_app_token: str = env.str("SBERCAT_APP_TOKEN")
    sbercat_redis_table: str = env.str("SBERCAT_REDIS_TABLE", default="sbercat-autousers-list")
    redis_user: str = env.str("REDIS_USER", default="default")
    redis_pass: str = env.str("REDIS_PASS", default="")
    redis_host: str = env.str("REDIS_HOST", default="localhost")
    redis_port: int = env.str("REDIS_PORT", default=6378)
    redis_connection_string: str = f"{redis_user}:{redis_pass}@{redis_host}:{redis_port}"
    app_port: int = env.int("APP_PORT", default=14880)
    superkey: str = env.str("SUPERKEY", default="kakdela???")

    base_dir: str = pathlib.Path.joinpath(pathlib.Path.cwd()).__str__()

    if not os.path.exists(f"{base_dir}/logs"):
        os.mkdir(f"{base_dir}/logs")

    class Config:
        env_file = ".env"


def get_config():
    _settings = Settings()
    return _settings


settings = get_config()
