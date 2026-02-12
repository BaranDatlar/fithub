from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "FitHub API"
    debug: bool = True

    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "fithub"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"

    # Cache TTLs (seconds)
    dashboard_cache_ttl: int = 120
    member_count_cache_ttl: int = 300
    member_search_cache_ttl: int = 300
    class_capacity_cache_ttl: int = 3600

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
