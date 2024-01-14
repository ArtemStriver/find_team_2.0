from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    CONTAINER_DB_PORT: int
    TEST_DB_NAME: str

    SECRET_KEY: str

    PGADMIN_DEFAULT_EMAIL: str
    PGADMIN_DEFAULT_PASSWORD: str

    class Config:
        env_file = ".env"

    @property
    def db_url_postgresql(self) -> str:
        """Создание url для БД"""
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

    @property
    def test_db_url_postgresql(self) -> str:
        """Создание url для тестовой БД"""
        if self.TEST_DB_NAME:
            return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
                    f"@{self.DB_HOST}:{self.DB_PORT}/{self.TEST_DB_NAME}")

        return self.db_url_postgresql


settings = Settings()
