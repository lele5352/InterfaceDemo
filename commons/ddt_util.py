"""
数据驱动引擎 - 支持 CSV 文件和 YAML 内联 parametrize 参数化
"""

import csv
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from commons.logger import logger
from commons.settings import PROJECT_ROOT


def load_csv(csv_path: str) -> List[Dict[str, str]]:
    """读取 CSV 文件，返回字典列表（每行一个字典）

    Args:
        csv_path: CSV 文件路径（支持绝对/相对路径）

    Returns:
        字典列表，每个字典的 key 为 CSV 表头，value 为对应的值
    """
    path = Path(csv_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / csv_path

    if not path.exists():
        logger.error(f"CSV 文件不存在: {path}")
        return []

    try:
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader]
        logger.info(f"CSV 加载成功: {path}, 共 {len(rows)} 条数据")
        return rows
    except Exception as e:
        logger.error(f"CSV 读取失败 [{path}]: {e}", exc_info=True)
        return []


def parse_parametrize(parametrize_data: List) -> Optional[Tuple[List[str], List[Any]]]:
    """解析 YAML 中的 parametrize 数据，返回 pytest 参数化格式

    YAML 格式:
        parametrize:
          - ["username", "password", "expected"]
          - ["user1", "pass1", "success"]
          - ["user2", "pass2", "fail"]

    Args:
        parametrize_data: YAML 中 parametrize 列表

    Returns:
        (param_names, param_values) 元组
        - param_names: 参数名列表 ["username", "password", "expected"]
        - param_values: 参数值列表 [["user1", "pass1", "success"], ...]
        如果数据无效返回 None
    """
    if not parametrize_data or not isinstance(parametrize_data, list) or len(parametrize_data) < 2:
        logger.warning(f"parametrize 数据不合法: {parametrize_data}")
        return None

    # 第一行为参数名
    param_names = parametrize_data[0]
    if not isinstance(param_names, list):
        logger.error(f"parametrize 第一行必须为参数名列表: {param_names}")
        return None

    # 后续行为参数值
    param_values = parametrize_data[1:]
    logger.info(f"参数化展开: 参数={param_names}, {len(param_values)} 组数据")

    # 转换为 pytest 参数化格式：argvalues 是列表的列表
    return param_names, param_values


def build_parametrize_from_csv(csv_path: str) -> Optional[Tuple[List[str], List[Any]]]:
    """通过 CSV 文件构建参数化数据

    使用场景: YAML 中 parametrize 是一个字符串路径指向 CSV 文件

    Args:
        csv_path: CSV 文件路径

    Returns:
        (param_names, param_values) 元组，内容同 parse_parametrize
    """
    rows = load_csv(csv_path)
    if not rows:
        return None

    param_names = list(rows[0].keys())
    param_values = [list(row.values()) for row in rows]

    logger.info(f"CSV 参数化展开: {csv_path}, 参数={param_names}, {len(param_values)} 组数据")
    return param_names, param_values


def guess_parametrize(raw_data) -> Optional[Tuple[List[str], List[Any]]]:
    """智能识别 parametrize 格式并展开

    支持两种格式:
    1. 内联列表: [["name", "pwd"], ["user1", "pass1"]]
    2. 字符串 CSV 路径: "data/login.csv"

    Args:
        raw_data: YAML 中 parametrize 的原始值

    Returns:
        标准化的 (param_names, param_values) 或 None
    """
    if raw_data is None:
        return None

    if isinstance(raw_data, list):
        return parse_parametrize(raw_data)

    if isinstance(raw_data, str) and raw_data.endswith(".csv"):
        return build_parametrize_from_csv(raw_data)

    logger.warning(f"不支持的 parametrize 格式: {type(raw_data)}")
    return None


def id_func(*args) -> str:
    """pytest 参数化 ID 生成函数 - 用于生成可读的测试 ID

    Returns:
        参数化用例标识字符串
    """
    val = args[0] if args else ""
    return f"[{val}]"
