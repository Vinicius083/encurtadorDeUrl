from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Encurtador de URL"
    api_base_url: str = "http://localhost:8000"
    jwt_secret: str = Field(default="troque-este-segredo")
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 24 * 7

    cassandra_hosts: str = "127.0.0.1"
    cassandra_port: int = 9042
    cassandra_keyspace: str = "url_shortener"
    cassandra_datacenter: str = "datacenter1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cassandra_contact_points(self) -> list[str]:
        return [host.strip() for host in self.cassandra_hosts.split(",") if host.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
