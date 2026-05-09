"""
HTTP 请求引擎 - 封装 requests.Session，支持变量替换、自动 Cookie 管理
"""

import re
from typing import Any, Dict, Optional

import requests
from requests import Response

from commons.logger import logger
from commons.settings import config
from commons.yaml_util import get_extract_value


class RequestEngine:
    """HTTP 请求引擎

    核心职责：
    1. 发送 HTTP 请求
    2. 自动替换请求中的变量占位符 ${env()}, ${func()}, ${read_yaml()}, $ddt{}
    3. 自动管理 Cookie / Session
    """

    # 变量占位符正则
    ENV_PATTERN = re.compile(r"\$\{env\((.+?)\)\}")
    FUNC_PATTERN = re.compile(r"\$\{(\w+)\(([^)]*)\)\}")
    READ_YAML_PATTERN = re.compile(r"\$\{read_yaml\((.+?)\)\}")
    DDT_PATTERN = re.compile(r"\$ddt\{(\w+)\}")

    def __init__(self):
        self.session = requests.Session()
        self._parametrize_context: Optional[Dict[str, Any]] = None

    def set_parametrize_context(self, context: Dict[str, Any]):
        """设置当前参数化上下文（用于 $ddt{} 替换）

        Args:
            context: 当前参数化数据行，如 {"username": "baili", "password": "baili123"}
        """
        self._parametrize_context = context

    # ==================== 变量替换 ====================

    def replace_variables(self, data: Any) -> Any:
        """递归替换数据中的变量占位符

        支持：
        - ${env(KEY)}: 环境变量
        - ${func_name(args)}: 热加载函数
        - $ddt{field}: 参数化变量
        - ${read_yaml(key)}: extract.yaml 读取

        Args:
            data: 原始数据（str/dict/list 均可）

        Returns:
            替换变量后的数据
        """
        if isinstance(data, str):
            return self._replace_in_string(data)
        elif isinstance(data, dict):
            return {k: self.replace_variables(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.replace_variables(item) for item in data]
        return data

    def _replace_in_string(self, value: str) -> str:
        """在单个字符串中替换所有变量占位符"""
        # 1. 替换 $ddt{}
        value = self.DDT_PATTERN.sub(self._replace_ddt, value)
        # 2. 替换 ${env()}
        value = self.ENV_PATTERN.sub(self._replace_env, value)
        # 3. 替换 ${read_yaml()}
        value = self.READ_YAML_PATTERN.sub(self._replace_read_yaml, value)
        # 4. 替换 ${func()}
        value = self.FUNC_PATTERN.sub(self._replace_func, value)
        return value

    def _replace_env(self, match: re.Match) -> str:
        """${env(KEY)} -> 环境变量值"""
        key = match.group(1).strip()
        value = config.get_env(key)
        if value is None:
            logger.warning(f"环境变量未定义: {key}")
            return match.group(0)
        return str(value)

    def _replace_ddt(self, match: re.Match) -> str:
        """$ddt{field} -> 参数化上下文中的值"""
        field = match.group(1).strip()
        if self._parametrize_context and field in self._parametrize_context:
            return str(self._parametrize_context[field])
        logger.warning(f"参数化变量未定义: $ddt{{{field}}}")
        return match.group(0)

    def _replace_read_yaml(self, match: re.Match) -> str:
        """${read_yaml(key)} -> extract.yaml 中的值"""
        key = match.group(1).strip()
        value = get_extract_value(key)
        if value is None:
            logger.warning(f"extract.yaml 中未找到: {key}")
            return match.group(0)
        return str(value)

    def _replace_func(self, match: re.Match) -> str:
        """${func_name(args)} -> 热加载函数返回值"""
        func_name = match.group(1).strip()
        raw_args = match.group(2).strip()
        args = [a.strip() for a in raw_args.split(",") if a.strip()]
        try:
            from debug_talk import DebugTalk
            dt = DebugTalk()
            func = getattr(dt, func_name, None)
            if func is None:
                logger.warning(f"debug_talk.py 中未定义函数: {func_name}")
                return match.group(0)
            result = func(*args)
            return str(result)
        except Exception as e:
            logger.error(f"热加载函数执行失败 {func_name}({args}): {e}", exc_info=True)
            return match.group(0)

    # ==================== 请求发送 ====================

    def send(self, method: str, url: str, **kwargs) -> Optional[Response]:
        """发送 HTTP 请求（自动变量替换）

        Args:
            method: HTTP 方法 (get/post/put/delete/patch)
            url: 请求 URL
            **kwargs: 其他 requests 参数 (params, data, json, headers, files, timeout, cookies 等)

        Returns:
            requests.Response 对象，失败返回 None
        """
        # 变量替换
        url = self.replace_variables(url)
        kwargs = self.replace_variables(kwargs)

        method = method.upper().strip()

        # 自动补全 base_url
        if not url.startswith(("http://", "https://")):
            base_url = config.get_base_url()
            if base_url:
                url = f"{base_url.rstrip('/')}/{url.lstrip('/')}"

        # 默认请求头
        if "headers" not in kwargs or not kwargs["headers"]:
            kwargs["headers"] = {}
        default_headers = config.get_headers()
        for k, v in default_headers.items():
            kwargs["headers"].setdefault(k, v)

        # 默认超时
        if "timeout" not in kwargs:
            kwargs["timeout"] = config.get_timeout()

        logger.info(f"➡️  {method} {url}")
        if kwargs.get("params"):
            logger.debug(f"   params: {kwargs['params']}")

        try:
            response = self.session.request(method, url, **kwargs)
            logger.info(f"⬅️  {response.status_code}")
            return response
        except requests.Timeout:
            logger.error(f"请求超时: {url}")
            raise
        except requests.ConnectionError:
            logger.error(f"连接失败: {url}")
            raise
        except Exception as e:
            logger.error(f"请求异常: {e}", exc_info=True)
            raise

    def close(self):
        """关闭会话"""
        self.session.close()


# 全局请求引擎实例
request_engine = RequestEngine()
