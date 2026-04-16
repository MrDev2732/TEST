from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FoodTruck SaaS API"
    app_env: str = "dev"
    app_debug: bool = True

    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/foodtruck"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


settings = Settings()
