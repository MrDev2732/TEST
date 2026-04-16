from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FoodTruck SaaS API"
    app_env: str = "dev"
    app_debug: bool = True

    database_url: str = ""

    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @model_validator(mode="after")
    def validate_security_sensitive_settings(self) -> "Settings":
        env = self.app_env.lower().strip()

        if env == "dev":
            if not self.database_url.strip():
                self.database_url = "postgresql+psycopg2://postgres:postgres@db:5432/foodtruck"
            if not self.jwt_secret_key.strip():
                self.jwt_secret_key = "dev-only-change-me"
            return self

        if not self.database_url.strip():
            raise ValueError("DATABASE_URL is required when APP_ENV is not dev")

        if not self.jwt_secret_key.strip():
            raise ValueError("JWT_SECRET_KEY is required when APP_ENV is not dev")

        weak_secrets = {
            "change-me",
            "secret",
            "super-secret-key",
            "jwt-secret",
            "password",
            "dev-only-change-me",
        }
        normalized_secret = self.jwt_secret_key.strip().lower()
        if normalized_secret in weak_secrets or len(self.jwt_secret_key.strip()) < 32:
            raise ValueError(
                "JWT_SECRET_KEY is too weak for non-dev environments. "
                "Use a unique random value with at least 32 characters."
            )

        return self


settings = Settings()
