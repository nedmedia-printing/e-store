from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    BASE_URL: str = "tdkgadisifoundation.com"
    SECRET_KEY: str = "aaaa"


def config_instance() -> Settings:
    return Settings()
