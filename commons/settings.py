"""
全局配置单例 - 管理环境变量、多环境配置、接口变量池
"""

import os
import threading
from pathlib import Path
from typing import Any, Optional

import yaml
from dotenv import load_dotenv

from commons.logger import logger

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

class ConfigSingleton:
    """全局配置单例，线程安全"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # 防止重复初始化
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._initialized = True
        self._env_vars: dict = {}       # run.env 加载的环境变量
        self._config: dict = {}         # config.yaml 加载的配置
        self._variable_pool: dict = {}  # 内存变量池（接口间传递）
        self._current_env: str = ''

        self._load_env_file()
        self._load_config()

    # ==================== 加载 run.env ====================

    def _load_env_file(self):
        """加载项目根目录的 run.env 文件"""
        env_path = PROJECT_ROOT / "run.env"
        if env_path.exists():
            load_dotenv(env_path, override=True)
            logger.info(f"环境变量已加载: {env_path}")
        else:
            logger.warning(f"未找到环境变量文件: {env_path}")

        # 收集所有环境变量到内存
        for key, value in os.environ.items():
            self._env_vars[key] = value

    # ==================== 加载 configs/config.yaml ====================

    def _load_config(self):
        """加载 configs/config.yaml 多环境配置"""
        config_path = PROJECT_ROOT / "configs" / "config.yaml"
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
            logger.info(f"配置文件已加载: {config_path}")
        else:
            logger.warning(f"未找到配置文件: {config_path}")

    # ==================== 公共 API ====================

    def get_env(self, key: str, default: Any = None) -> str:
        """获取环境变量（来自 run.env 或系统环境）"""
        return os.getenv(key, self._env_vars.get(key, default))

    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置项（来自 config.yaml）"""
        return self._config.get(key, default)

    def get_base_url(self) -> str:
        """获取当前环境的 base_url"""
        env = self._current_env
        base_urls = self._config.get("base_urls", {})
        url = base_urls.get(env, "")
        if not url:
            logger.warning(f"未找到环境 [{env}] 的 base_url")
        return url

    def get_headers(self) -> dict:
        """获取当前环境的默认请求头"""
        env = self._current_env
        headers = self._config.get("headers", {})
        return headers.get(env, {"Content-Type": "application/json"})

    def get_timeout(self) -> int:
        """获取请求超时时间（秒）"""
        return self._config.get("timeout", 30)

    def set_env(self, env_name: str):
        """切换当前环境（dev/test/prod）"""
        if env_name in self._config.get("base_urls", {}):
            self._current_env = env_name
            logger.info(f"环境已切换至: {env_name}")
        else:
            logger.warning(f"未知环境: {env_name}，当前可用: {list(self._config.get('base_urls', {}).keys())}")

    @property
    def current_env(self) -> str:
        return self._current_env

    # ==================== 变量池（接口间传递） ====================

    def set_variable(self, key: str, value: Any):
        """设置变量到内存池"""
        self._variable_pool[key] = value

    def get_variable(self, key: str, default: Any = None) -> Any:
        """从内存池获取变量"""
        return self._variable_pool.get(key, default)

    def clear_variable_pool(self):
        """清空变量池"""
        self._variable_pool.clear()


# 全局唯一实例
# config = ConfigSingleton()

if __name__ == "__main__":
    config_singleton = ConfigSingleton()

