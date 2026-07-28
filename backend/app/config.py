from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación, cargada desde variables de entorno (.env)."""

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int
    database_url: str
    test_database_url: str
    cors_origins: str = "http://localhost:5173"
    secret_key: str
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def cors_origins_list(self) -> list[str]:
        """Convierte CORS_ORIGINS (string separado por comas) en una lista de orígenes."""
        return [origen.strip() for origen in self.cors_origins.split(",") if origen.strip()]


settings = Settings()
