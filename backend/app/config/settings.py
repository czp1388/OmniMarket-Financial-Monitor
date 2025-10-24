# 项目配置
class Settings:
    PROJECT_NAME = "寰宇多市场金融监控系统"
    VERSION = "0.1.0"
    API_V1_STR = "/api/v1"
    
    # 数据源配置
    DATA_SOURCES = {
        "crypto": ["binance", "okx", "bybit"],
        "stock": ["tushare", "akshare"], 
        "forex": ["dukascopy", "oanda"]
    }

settings = Settings()
