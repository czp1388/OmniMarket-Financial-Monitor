from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "OmniMarket Financial Monitor"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/omnimarket"
    INFLUXDB_URL: str = "http://localhost:8086"
    INFLUXDB_TOKEN: str = "your-influxdb-token"
    INFLUXDB_ORG: str = "omnimarket"
    INFLUXDB_BUCKET: str = "market_data"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    
    # API密钥配置
    BINANCE_API_KEY: str = ""
    BINANCE_SECRET_KEY: str = ""
    BYBIT_API_KEY: str = ""
    BYBIT_SECRET_KEY: str = ""
    TUSHARE_TOKEN: str = ""
    ALPHA_VANTAGE_API_KEY: str = ""  # Alpha Vantage API密钥
    
    # 数据配置
    DATA_UPDATE_INTERVAL: int = 60  # 数据更新间隔（秒）
    MAX_HISTORICAL_DAYS: int = 365  # 最大历史数据天数
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 邮件通知配置
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""
    
    # Telegram通知配置
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    
    # Webhook配置
    WEBHOOK_URL: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局设置实例
settings = Settings()
