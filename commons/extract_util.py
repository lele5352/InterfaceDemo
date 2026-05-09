"""
响应数据提取引擎 - 支持 JSONPath 和正则表达式提取
"""

import re
from typing import Any, List, Optional, Tuple, Union

import jsonpath

from commons.logger import logger
from commons.settings import config
from commons.yaml_util import write_extract_yaml


class ExtractEngine:
    """响应数据提取引擎

    支持两种提取方式:
    1. JSONPath 提取: [json, "$.data.token", 0]
    2. 正则提取:     [text, '"token":"(.*?)"', 1]
    """

    def extract(self, response, extract_config: dict) -> dict:
        """执行响应数据提取

        config 格式:
            var_name: [json, "$.data.token", 0]     # JSONPath + 索引
            var_name: [text, '"token":"(.*?)"', 1]   # 正则 + 分组索引

        Args:
            response: requests.Response 对象
            extract_config: 提取配置字典

        Returns:
            提取结果字典 {var_name: value, ...}
        """
        if not extract_config:
            return {}

        results = {}
        for key, conf in extract_config.items():
            if not isinstance(conf, (list, tuple)) or len(conf) < 2:
                logger.warning(f"提取配置格式错误: {key}={conf}")
                continue

            method = conf[0]        # "json" 或 "text"
            rule = conf[1]          # JSONPath 或 正则
            index = int(conf[2]) if len(conf) > 2 else 0  # 提取索引/分组

            value = self._extract(response, method, rule, index)
            if value is not None:
                results[key] = value
                logger.info(f"提取成功: {key}={value}")

                # 写入 extract.yaml 和内存变量池
                self._save_extracted(key, value)

        return results

    def _extract(self, response, method: str, rule: str, index: int) -> Any:
        """根据提取方式执行提取

        Args:
            response: requests.Response 对象
            method: 提取方式 (json/text)
            rule: 提取规则 (JSONPath/正则表达式)
            index: 结果索引 / 正则分组索引

        Returns:
            提取的值，失败返回 None
        """
        try:
            if method == "json":
                return self._extract_by_json(response, rule, index)
            elif method == "text":
                return self._extract_by_regex(response, rule, index)
            else:
                logger.error(f"不支持的提取方式: {method}（仅支持 json/text）")
                return None
        except Exception as e:
            logger.error(f"提取异常 [{method}] rule={rule}: {e}", exc_info=True)
            return None

    def _extract_by_json(self, response, jsonpath_expr: str, index: int) -> Any:
        """JSONPath 提取

        Args:
            response: requests.Response 对象
            jsonpath_expr: JSONPath 表达式，如 "$.data.token"
            index: 结果列表中的索引

        Returns:
            提取的值
        """
        try:
            data = response.json()
        except ValueError:
            logger.error("响应不是有效的 JSON 格式")
            return None

        result = jsonpath.jsonpath(data, jsonpath_expr)
        if result is False:
            logger.error(f"JSONPath 未匹配: {jsonpath_expr}")
            return None

        if isinstance(result, list) and index < len(result):
            return result[index]

        logger.error(f"JSONPath 索引超界: index={index}, 长度={len(result) if isinstance(result, list) else 1}")
        return result[0] if result else None

    def _extract_by_regex(self, response, pattern: str, group_index: int) -> Any:
        """正则表达式提取

        Args:
            response: requests.Response 对象
            pattern: 正则表达式，如 '"token":"(.*?)"'
            group_index: 分组索引，0=完整匹配, 1=第一个分组

        Returns:
            提取的值
        """
        text = response.text
        match = re.search(pattern, text)
        if not match:
            logger.error(f"正则未匹配: {pattern}")
            return None

        if group_index > match.lastindex:
            logger.error(f"正则分组索引超界: group_index={group_index}, lastindex={match.lastindex}")
            return None

        return match.group(group_index)

    def _save_extracted(self, key: str, value: Any):
        """保存提取结果到 extract.yaml 和内存变量池"""
        write_extract_yaml({key: value})

        # 写入内存变量池
        config.set_variable(key, value)

    def extract_response_info(self, response, extract_info: dict) -> dict:
        """兼容旧接口 - 提取响应中的关联字段信息

        Args:
            response: requests.Response 对象
            extract_info: 提取配置字典

        Returns:
            提取结果字典
        """
        return self.extract(response, extract_info)


# 全局提取引擎实例
extract_engine = ExtractEngine()
