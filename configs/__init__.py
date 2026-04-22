import os
from . import dev_config, test_config, prod_config

PROJECT_NAME = {
    "allure_project_name": "聚合接口测试"
}

# 获取运行环境（默认测试环境）
ENV = os.getenv("SYSTEM_ENV", "test")

# 根据环境加载对应配置
if ENV == "dev":
    current_config = dev_config
elif ENV == "test":
    current_config = test_config
elif ENV == "prod":
    current_config = prod_config
else:
    raise ValueError(f"不支持的环境类型: {ENV}，可选值：dev/test/prod")

# 统一导出配置（方便业务代码导入）
DB_CONFIG = current_config.DB_CONFIG
URL_CONFIG = current_config.URL_CONFIG
REDIS_CONFIG = current_config.REDIS_CONFIG