from datetime import timedelta
from pathlib import Path
from typing import List

from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from slowapi import Limiter
from slowapi.util import get_remote_address


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Project
    PROJECT_NAME: str = "SentinelAI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Enterprise AI-Powered Security Operations Center Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # API
    API_V1_STR: str = "/api/v1"
    API_KEY: str = ""
    API_KEY_NAME: str = "X-API-Key"

    # Security
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_REFRESH_SECRET_KEY: str = ""
    JWT_AUDIENCE: str = "sentinelai-api"
    JWT_ISSUER: str = "sentinelai"
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_MAX_LENGTH: int = 128
    BCRYPT_ROUNDS: int = 12
    MFA_ENABLED: bool = False
    MFA_ISSUER_NAME: str = "SentinelAI"
    SESSION_TIMEOUT_MINUTES: int = 60
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v

    TRUSTED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1",
        "sentinelai.dev",
    ]

    @field_validator("TRUSTED_HOSTS", mode="before")
    @classmethod
    def parse_trusted_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "sentinelai"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "sentinelai"
    DATABASE_URL: PostgresDsn | None = None
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 1800
    DATABASE_ECHO: bool = False
    DATABASE_SSL_ENABLED: bool = False

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v, info):
        if v:
            return v
        values = info.data
        url = f"postgresql+asyncpg://{values['POSTGRES_USER']}:{values['POSTGRES_PASSWORD']}@{values['POSTGRES_SERVER']}:{values['POSTGRES_PORT']}/{values['POSTGRES_DB']}"
        return url

    DATABASE_TEST_URL: PostgresDsn | None = None

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    REDIS_URL: RedisDsn | None = None

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_url(cls, v, info):
        if v:
            return v
        values = info.data
        password = f":{values['REDIS_PASSWORD']}@" if values.get("REDIS_PASSWORD") else ""
        url = f"redis://{password}{values['REDIS_HOST']}:{values['REDIS_PORT']}/{values['REDIS_DB']}"
        return url

    # AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/embedding-001"
    GEMINI_MAX_TOKENS: int = 8192
    GEMINI_TEMPERATURE: float = 0.2
    AI_ENABLED: bool = True
    AI_RATE_LIMIT_PER_MINUTE: int = 60
    AI_BATCH_SIZE: int = 10
    AI_CACHE_TTL_SECONDS: int = 3600
    AI_FALLBACK_MODEL: str = "gemini-1.5-flash-8b"

    # Logging & Monitoring
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AI: str = "10/minute"
    RATE_LIMIT_AUTH: str = "5/minute"
    RATE_LIMIT_API: str = "1000/hour"

    @property
    def rate_limiter(self):
        return Limiter(key_func=get_remote_address)

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 1000
    WS_MESSAGE_QUEUE_SIZE: int = 10000

    # File Upload
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024
    ALLOWED_EXTENSIONS: List[str] = [
        ".log", ".txt", ".csv", ".json", ".xml", ".evtx",
        ".pcap", ".cap", ".pcapng", ".dmp", ".zip", ".gz",
    ]
    UPLOAD_DIR: Path = Path("uploads")

    # Detection Engine
    DETECTION_ENGINE_INTERVAL: int = 60
    DETECTION_RULES_DIR: Path = Path("rules")
    DETECTION_MAX_SIGNATURES: int = 10000
    DETECTION_CACHE_SIZE: int = 1000
    MITRE_ATTACK_DATA_URL: str = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"

    # Incident Response
    INCIDENT_AUTO_RESOLVE_DAYS: int = 30
    INCIDENT_MAX_PRIORITY: int = 5
    INCIDENT_SEVERITY_LEVELS: List[str] = [
        "critical", "high", "medium", "low", "informational",
    ]

    # Reports
    REPORT_MAX_SCHEDULES: int = 50
    REPORT_GENERATION_TIMEOUT: int = 300
    REPORT_STORAGE_DAYS: int = 90
    REPORT_FORMATS: List[str] = ["pdf", "csv", "json", "html", "xlsx"]

    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = ""
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str = "SentinelAI"

    # Webhook
    WEBHOOK_RETRY_MAX: int = 3
    WEBHOOK_RETRY_DELAY: int = 10
    WEBHOOK_TIMEOUT: int = 30
    WEBHOOK_MAX_PAYLOAD_SIZE: int = 1024 * 1024

    # SIEM Integration
    SIEM_EVENT_BATCH_SIZE: int = 1000
    SIEM_EVENT_BUFFER_SECONDS: int = 5
    SIEM_MAX_EVENTS_PER_SECOND: int = 100000
    SIEM_RETENTION_DAYS: int = 90
    SIEM_HOT_DATA_DAYS: int = 7
    SIEM_WARM_DATA_DAYS: int = 30

    # Elasticsearch (optional)
    ELASTICSEARCH_ENABLED: bool = False
    ELASTICSEARCH_HOSTS: List[str] = ["http://localhost:9200"]
    ELASTICSEARCH_INDEX_PREFIX: str = "sentinelai"

    @property
    def JWT_ACCESS_TOKEN_EXPIRE(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def JWT_REFRESH_TOKEN_EXPIRE(self) -> timedelta:
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)


settings = Settings()
