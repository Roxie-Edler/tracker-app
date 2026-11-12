
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    JWT_SECRET = os.getenv("JWT_SECRET", SECRET_KEY)

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///dev.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "sqlite://"
    )


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
