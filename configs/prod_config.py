# 数据库连接配置（生产环境建议从环境变量读取，避免硬编码）
import os

DB_CONFIG = {
    "host": os.getenv("PROD_DB_HOST"),
    "port": int(os.getenv("PROD_DB_PORT", 3306)),
    "user": os.getenv("PROD_DB_USER"),
    "password": os.getenv("PROD_DB_PASSWORD"),
    "database": os.getenv("PROD_DB_NAME")
}

# URL 环境配置
URL_CONFIG = {
    "base_url": os.getenv("PROD_BASE_URL"),
    "api_prefix": "/api/v1"
}

# 其他系统环境变量
REDIS_CONFIG = {
    "host": os.getenv("PROD_REDIS_HOST"),
    "port": int(os.getenv("PROD_REDIS_PORT", 6379)),
    "db": int(os.getenv("PROD_REDIS_DB", 0))
}

TIMEOUT = 10